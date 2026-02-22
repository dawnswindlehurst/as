"""Historical data population job for Scorealarm."""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from database.db import get_db_session
from database.scorealarm_models import (
    ScorealarmSport, ScorealarmCategory, ScorealarmTournament,
    ScorealarmSeason, ScorealarmTeam, ScorealarmMatch, ScorealarmScore
)
from scrapers.superbet.superbet_client import SuperbetClient
from scrapers.superbet.scorealarm_client import ScorealarmClient
from utils.gentle_rate_limiter import GentleRateLimiter
from utils.checkpoint import CheckpointManager
from utils.logger import log

# Constants
MAX_TEAM_NAME_LENGTH = 50
ALLOWED_MATCH_YEARS = {2024, 2025, 2026}
FOOTBALL_SUPERBET_SPORT_ID = 5

# Superbet sport ids to keep in historical population (user-curated allowlist)
ALLOWED_POPULATE_SUPERBET_SPORT_IDS = {
    1,    # Vôlei
    2,    # Tênis
    3,    # Hóquei no Gelo
    4,    # Basquete
    5,    # Futebol
    6,    # Sinuca
    7,    # Bandy
    8,    # Rúgbi
    9,    # Floorball
    11,   # Handebol
    12,   # Futebol Americano
    13,   # Dardos
    15,   # Polo aquático
    17,   # Futsal
    19,   # Futebol australiano
    20,   # Beisebol
    24,   # Tênis de Mesa
    39,   # League of Legends
    54,   # Dota 2
    55,   # Counter-Strike 2
    80,   # Rainbow Six
    153,  # Valorant
}


class HistoricalPopulateJob:
    """Popula database com TODO histórico disponível."""
    
    def __init__(self):
        self.superbet_client = SuperbetClient()
        self.scorealarm_client = ScorealarmClient()
        self.limiter = GentleRateLimiter(
            requests_per_minute=10,
            delay_between_requests=3.0,
            delay_between_sports=30,
            delay_between_tournaments=5,
            night_mode_speedup=True
        )
        # Expira checkpoint após 1h para permitir descoberta contínua de novos jogos.
        self.checkpoint = CheckpointManager(max_age_hours=1)
        self.db = get_db_session()
        self.excluded_season_ids = self._load_excluded_seasons()
    
    async def run(self):
        """Executa populamento completo."""
        self.limiter.start_time = datetime.now(timezone.utc)
        checkpoint_data = self.checkpoint.load()
        stats = checkpoint_data["stats"]
        
        log.info("="*60)
        log.info("🐢 INICIANDO POPULAMENTO HISTÓRICO (MODO GENTIL)")
        log.info("⏱️ Estimativa: 4-8 horas")
        log.info("💡 Pode interromper a qualquer momento - checkpoint salva progresso")
        log.info("="*60)
        
        try:
            # Initialize clients with context managers
            async with self.superbet_client as superbet:
                async with self.scorealarm_client as scorealarm:
                    # 1. Buscar todos os esportes
                    sports = await superbet.get_sports()
                    await self.limiter.wait()

                    sports = [
                        sport for sport in sports
                        if sport.id in ALLOWED_POPULATE_SUPERBET_SPORT_IDS
                    ]
                    
                    total_sports = len(sports)
                    log.info(
                        f"📊 Total de esportes permitidos para coleta: {total_sports} "
                        f"(allowlist size={len(ALLOWED_POPULATE_SUPERBET_SPORT_IDS)})"
                    )
                    
                    for i, sport in enumerate(sports):
                        log.info(f"\n{'='*50}")
                        log.info(f"📊 [{i+1}/{total_sports}] {sport.name}")
                        log.info(f"📈 Stats: {self.limiter.get_stats()}")
                        log.info(f"{'='*50}")
                        
                        stats["sports"] += 1
                        
                        # Salvar esporte no DB
                        await self._save_sport(sport)
                        
                        # Buscar o ID do banco após salvar (superbet_id -> db id)
                        db_sport = self.db.query(ScorealarmSport).filter(
                            ScorealarmSport.superbet_id == sport.id
                        ).first()
                        
                        if not db_sport:
                            log.error(f"❌ Sport not found in database after saving: {sport.name} (superbet_id={sport.id})")
                            continue
                        
                        db_sport_id = db_sport.id  # Use this database ID, not sport.id from the API
                        
                        # Processar torneios do esporte
                        await self._process_sport_tournaments(
                            sport, db_sport_id, checkpoint_data, stats, superbet, scorealarm
                        )
                        
                        # Marcar esporte como completo
                        self.checkpoint.mark_sport_complete(checkpoint_data, sport.id)
                        
                        # Pausa entre esportes
                        await self.limiter.wait_between_sports()
                        
                        # Log progresso
                        log.info(f"✅ {sport.name} completo!")
                        log.info(f"📊 Progresso: {stats}")
            
            # Fim
            elapsed = datetime.now(timezone.utc) - self.limiter.start_time
            log.info(f"\n{'='*60}")
            log.info(f"🏁 POPULAMENTO COMPLETO!")
            log.info(f"⏱️ Tempo total: {elapsed}")
            log.info(f"📊 Stats finais: {stats}")
            log.info(f"{'='*60}")
            
        except KeyboardInterrupt:
            log.info("\n⚠️ Interrompido pelo usuário. Progresso salvo!")
            log.info(f"📊 Stats até agora: {stats}")
        except Exception as e:
            log.error(f"❌ Erro fatal: {e}")
            log.info("💾 Checkpoint salvo. Rode novamente para continuar.")
            raise
        finally:
            self._save_excluded_seasons()
            self.db.close()
    
    async def _process_sport_tournaments(
        self, sport, db_sport_id: int, checkpoint_data: dict, stats: dict, superbet, scorealarm
    ):
        """Processa todos os torneios de um esporte."""
        try:
            tournaments = await superbet.get_tournaments_by_sport(sport.id)
            await self.limiter.wait()
            log.info(f"🏟️ {sport.name}: {len(tournaments)} torneios encontrados")

            if not tournaments:
                log.warning(f"⚠️ {sport.name}: nenhum torneio retornado pela API")
                return

            processed_in_sport = 0
            
            for idx, tournament in enumerate(tournaments, start=1):
                stats["tournaments"] += 1
                processed_in_sport += 1
                log.info(
                    f"🏆 [{idx}/{len(tournaments)}] {sport.name} -> {tournament.tournament_name} "
                    f"(id={tournament.tournament_id})"
                )
                
                try:
                    # Salvar torneio
                    await self._save_tournament(tournament, db_sport_id)
                    
                    # Buscar detalhes (seasons)
                    details = await scorealarm.get_tournament_details(tournament.tournament_id)
                    await self.limiter.wait()
                    
                    if not details:
                        log.warning(f"⚠️ Sem detalhes para {tournament.tournament_name}")
                        self.checkpoint.mark_tournament_complete(checkpoint_data, tournament.tournament_id)
                        continue

                    log.info(
                        f"🗂️ {tournament.tournament_name}: {len(details.seasons)} seasons "
                        f"(competition_id={details.competition_id})"
                    )
                    
                    # Processar cada season
                    api_tournament_matches = 0
                    season_matches_to_save = []
                    for season in details.seasons:
                        if season.id in self.excluded_season_ids:
                            log.info(
                                f"⏭️ {tournament.tournament_name} / {season.name} (id={season.id}) "
                                "em lista de exclusão"
                            )
                            continue
                        stats["seasons"] += 1
                        await self._save_season(season, tournament.tournament_id)
                        
                        # Buscar matches da season
                        matches = await scorealarm.get_competition_events(
                            season_id=season.id,
                            competition_id=details.competition_id
                        )
                        await self.limiter.wait()
                        filtered_matches = self._filter_matches_by_year(matches)
                        api_tournament_matches += len(filtered_matches)
                        log.info(
                            f"📅 {tournament.tournament_name} / {season.name} (id={season.id}): "
                            f"{len(filtered_matches)} partidas em {sorted(ALLOWED_MATCH_YEARS)}"
                        )

                        season_matches_to_save.append((season.id, filtered_matches))

                    db_tournament_matches = self._get_db_tournament_match_count(tournament.tournament_id)
                    if db_tournament_matches == api_tournament_matches:
                        log.info(
                            f"⏭️ {tournament.tournament_name}: sem atualização "
                            f"(DB={db_tournament_matches}, API={api_tournament_matches})"
                        )
                    else:
                        log.info(
                            f"🔄 {tournament.tournament_name}: atualização necessária "
                            f"(DB={db_tournament_matches}, API={api_tournament_matches})"
                        )
                        for season_id, filtered_matches in season_matches_to_save:
                            for match in filtered_matches:
                                inserted = await self._save_match(
                                    match,
                                    db_sport_id,
                                    tournament.tournament_id,
                                    season_id,
                                    sport,
                                    scorealarm,
                                )
                                if inserted:
                                    stats["matches"] += 1
                    
                    # Marcar torneio como completo
                    self.checkpoint.mark_tournament_complete(checkpoint_data, tournament.tournament_id)
                    
                    # Pausa entre torneios
                    await self.limiter.wait_between_tournaments()
                    
                except Exception as e:
                    stats["errors"] += 1
                    log.error(f"❌ Erro em {tournament.tournament_name}: {e}")
                    continue

            if processed_in_sport == 0:
                log.info(f"ℹ️ {sport.name}: todos os torneios já estavam no checkpoint")
                    
        except Exception as e:
            stats["errors"] += 1
            log.error(f"❌ Erro ao buscar torneios de {sport.name}: {e}")
    
    async def _save_sport(self, sport):
        """Salva ou atualiza esporte no DB."""
        existing = self.db.query(ScorealarmSport).filter(
            ScorealarmSport.superbet_id == sport.id
        ).first()
        
        if not existing:
            db_sport = ScorealarmSport(
                name=sport.name,
                superbet_id=sport.id,
                is_gold=sport.id in self._get_gold_sports()
            )
            self.db.add(db_sport)
            self.db.commit()
    
    async def _save_tournament(self, tournament, sport_id: int):
        """Salva ou atualiza torneio no DB."""
        existing = self.db.query(ScorealarmTournament).filter(
            ScorealarmTournament.id == tournament.tournament_id
        ).first()
        
        if not existing:
            db_tournament = ScorealarmTournament(
                id=tournament.tournament_id,
                name=tournament.tournament_name,
                sport_id=sport_id
            )
            self.db.add(db_tournament)
            self.db.commit()
    
    async def _save_season(self, season, tournament_id: int):
        """Salva ou atualiza season no DB."""
        existing = self.db.query(ScorealarmSeason).filter(
            ScorealarmSeason.id == season.id
        ).first()
        
        if not existing:
            db_season = ScorealarmSeason(
                id=season.id,
                name=season.name,
                tournament_id=tournament_id,
                is_current=False  # Default to False; can be updated by sync jobs
            )
            self.db.add(db_season)
            self.db.commit()
    
    async def _save_match(
        self,
        match,
        sport_id: int,
        tournament_id: int,
        season_id: int,
        sport,
        scorealarm,
    ) -> bool:
        """Salva ou atualiza match no DB."""
        existing = self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.platform_id == match.platform_id
        ).first()
        
        if existing:
            if sport.id == FOOTBALL_SUPERBET_SPORT_ID:
                if self._has_football_extra_data(existing):
                    return False

                await self._enrich_football_match_inline(existing, scorealarm)
                self.db.commit()
            return False  # Já existe
        
        # Salvar times se não existirem
        team1_id = await self._save_team(match.team1, sport_id)
        team2_id = await self._save_team(match.team2, sport_id)
        
        # Get final scores from match data
        # Score type 0 represents the final score in most sports
        team1_score = None
        team2_score = None
        if match.scores:
            final_score = next((s for s in match.scores if s.type == 0), None)
            if final_score:
                team1_score = final_score.team1
                team2_score = final_score.team2
        
        db_match = ScorealarmMatch(
            platform_id=match.platform_id,
            offer_id=match.offer_id,
            sport_id=sport_id,
            tournament_id=tournament_id,
            season_id=season_id,
            team1_id=team1_id,
            team2_id=team2_id,
            match_date=match.match_date,
            match_status=match.match_status,
            team1_score=team1_score,
            team2_score=team2_score,
            is_finished=match.match_status == 100  # 100 = finished
        )
        self.db.add(db_match)
        self.db.commit()

        if sport.id == FOOTBALL_SUPERBET_SPORT_ID:
            await self._enrich_football_match_inline(db_match, scorealarm)
            self.db.commit()
        
        # Salvar scores por período se existirem
        if match.scores:
            for score in match.scores:
                await self._save_score(db_match.id, score)
        return True

    async def _enrich_football_match_inline(self, db_match, scorealarm):
        """Enriquece partidas de futebol durante o populate via chamada V2."""
        fixture_id = db_match.offer_id
        if not fixture_id:
            return

        fixture_stats = await scorealarm.get_fixture_stats(fixture_id, sport_hint="soccer")
        await self.limiter.wait()

        if not fixture_stats:
            db_match.enriched_at = datetime.now(timezone.utc)
            return

        match_stats = fixture_stats.match_stats or []
        live_events = fixture_stats.live_events or []

        if match_stats:
            db_match.match_stats_raw = [
                {
                    "type": stat.type,
                    "team1": stat.team1,
                    "team2": stat.team2,
                    "stat_name": stat.stat_name,
                }
                for stat in match_stats
            ]

        if live_events:
            db_match.live_events_raw = [
                {
                    "type": event.type,
                    "subtype": event.subtype,
                    "minute": event.minute,
                    "added_time": event.added_time,
                    "side": event.side,
                    "player_id": event.player_id,
                    "player_name": event.player_name,
                    "secondary_player_id": event.secondary_player_id,
                    "secondary_player_name": event.secondary_player_name,
                    "score": event.score,
                }
                for event in live_events
            ]

        self._extract_football_stats(db_match, match_stats, live_events)
        db_match.enriched_at = datetime.now(timezone.utc)

    def _extract_football_stats(self, db_match, match_stats, live_events):
        """Extrai métricas de futebol (xG, finalizações no alvo, escanteios, gols)."""
        xg_stat = next((stat for stat in match_stats if stat.type == 19), None)
        if xg_stat:
            try:
                db_match.xg_home = float(xg_stat.team1) if xg_stat.team1 else None
                db_match.xg_away = float(xg_stat.team2) if xg_stat.team2 else None
            except (ValueError, TypeError):
                db_match.xg_home = None
                db_match.xg_away = None

        shots_stat = next((stat for stat in match_stats if stat.type == 2), None)
        if shots_stat:
            try:
                db_match.shots_on_goal_home = int(shots_stat.team1) if shots_stat.team1 else None
                db_match.shots_on_goal_away = int(shots_stat.team2) if shots_stat.team2 else None
            except (ValueError, TypeError):
                db_match.shots_on_goal_home = None
                db_match.shots_on_goal_away = None

        corners_stat = next((stat for stat in match_stats if stat.type == 5), None)
        if corners_stat:
            try:
                db_match.corners_home = int(corners_stat.team1) if corners_stat.team1 else None
                db_match.corners_away = int(corners_stat.team2) if corners_stat.team2 else None
            except (ValueError, TypeError):
                db_match.corners_home = None
                db_match.corners_away = None

        goal_events = [event for event in live_events if event.type == 4]
        if goal_events:
            db_match.goal_events = [
                {
                    "minute": event.minute,
                    "added_time": event.added_time,
                    "player_id": event.player_id,
                    "player_name": event.player_name,
                    "assist_player_id": event.secondary_player_id,
                    "assist_player_name": event.secondary_player_name,
                    "side": event.side,
                    "score": event.score,
                }
                for event in goal_events
            ]

    def _filter_matches_by_year(self, matches: list) -> list:
        """Mantém apenas partidas com ano permitido."""
        filtered = []
        for match in matches:
            match_date = getattr(match, "match_date", None)
            if match_date and match_date.year in ALLOWED_MATCH_YEARS:
                filtered.append(match)
        return filtered

    def _get_db_tournament_match_count(self, tournament_id: int) -> int:
        """Conta partidas do torneio no intervalo de anos permitido."""
        return self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.tournament_id == tournament_id,
            ScorealarmMatch.match_date.isnot(None),
            ScorealarmMatch.match_date >= datetime(2024, 1, 1, tzinfo=timezone.utc),
            ScorealarmMatch.match_date < datetime(2027, 1, 1, tzinfo=timezone.utc),
        ).count()
    

    def _name_has_old_year(self, name: str) -> bool:
        """Verifica se o nome contém ano entre 1980 e 2023."""
        return bool(name and OLD_YEAR_NAME_PATTERN.search(name))

    def _load_excluded_seasons(self) -> set[int]:
        """Carrega IDs de seasons excluídas de execuções anteriores."""
        try:
            if EXCLUDED_SEASONS_FILE.exists():
                with open(EXCLUDED_SEASONS_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                season_ids = data.get("season_ids", [])
                return {int(season_id) for season_id in season_ids}
        except Exception as exc:
            log.warning(f"⚠️ Falha ao carregar exclusões de season: {exc}")
        return set()

    def _save_excluded_seasons(self):
        """Persista IDs de seasons excluídas para pulos futuros."""
        EXCLUDED_SEASONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {"season_ids": sorted(self.excluded_season_ids)}
        with open(EXCLUDED_SEASONS_FILE, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)

    def _exclude_season(self, season_id: int, season_name: str):
        """Adiciona season à lista de exclusão persistente."""
        if season_id in self.excluded_season_ids:
            return

        self.excluded_season_ids.add(season_id)
        self._save_excluded_seasons()
        log.info(
            f"🚫 Season adicionada à exclusão: {season_name} (id={season_id}) "
            "por ano antigo e 0 jogos no recorte 2024-2026"
        )

    async def _save_team(self, team, sport_id: int) -> int:
        """Salva ou retorna ID do time."""
        # Try to find by axilis_id constructed from team.id
        axilis_id = f"ax:team:{team.id}"
        existing = self.db.query(ScorealarmTeam).filter(
            ScorealarmTeam.axilis_id == axilis_id
        ).first()
        
        if existing:
            return existing.id
        
        # Truncate team name if needed
        short_name = team.name[:MAX_TEAM_NAME_LENGTH] if len(team.name) > MAX_TEAM_NAME_LENGTH else team.name
        
        db_team = ScorealarmTeam(
            name=team.name,
            short_name=short_name,
            sport_id=sport_id,
            axilis_id=axilis_id
        )
        self.db.add(db_team)
        self.db.commit()
        return db_team.id
    
    async def _save_score(self, match_id: int, score):
        """Salva score de período."""
        db_score = ScorealarmScore(
            match_id=match_id,
            period_type=f"type_{score.type}",
            period_number=score.type,
            team1_score=score.team1,
            team2_score=score.team2
        )
        self.db.add(db_score)
        self.db.commit()
    
    def _get_gold_sports(self) -> list:
        """IDs de esportes 'gold' (menos analisados = mais edge)."""
        return [
            20,   # Bandy
            48,   # Beach Soccer
            43,   # Curling
            60,   # Floorball
            61,   # Futsal
            71,   # Handball
            108,  # Snooker
            115,  # Table Tennis
            142,  # Water Polo
            # Adicionar mais conforme identificados
        ]


async def main():
    """Entry point."""
    job = HistoricalPopulateJob()
    await job.run()


if __name__ == "__main__":
    asyncio.run(main())

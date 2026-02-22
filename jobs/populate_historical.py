"""Historical data population job for Scorealarm."""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
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
BASKETBALL_SPORT_ID = 4
TENNIS_SPORT_ID = 2
VOLLEYBALL_SPORT_ID = 1
HOCKEY_SPORT_ID = 3
HANDBALL_SPORT_ID = 11
BASEBALL_SPORT_ID = 20
WATER_POLO_SPORT_ID = 15
TABLE_TENNIS_SPORT_ID = 24
RUGBY_SPORT_ID = 8
BANDY_SPORT_ID = 7

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
        scorealarm: Optional["ScorealarmClient"] = None,
    ) -> bool:
        """Salva ou atualiza match no DB."""
        existing = self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.platform_id == match.platform_id
        ).first()
        
        if existing:
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
        
        # Fetch and save detailed match data for finished matches
        if match.match_status == 100 and scorealarm and match.platform_id:
            await self._fetch_and_save_match_detail(db_match, match.platform_id, scorealarm)

        # Salvar scores por período se existirem
        if match.scores:
            for score in match.scores:
                await self._save_score(db_match.id, score)
        return True

    async def _fetch_and_save_match_detail(
        self, db_match: ScorealarmMatch, platform_id: str, scorealarm
    ) -> None:
        """Fetch raw event detail and persist all detailed fields to db_match."""
        try:
            raw = await scorealarm.get_match_detail_raw(platform_id)
            if not raw:
                return
            match_data = raw.get('match', raw)
            generic = self._extract_generic_stats(match_data)
            for key, value in generic.items():
                if value is not None:
                    setattr(db_match, key, value)

            sport_id = db_match.sport_id
            # Basketball
            if sport_id == BASKETBALL_SPORT_ID:
                bball = self._extract_basketball_stats(raw.get('statistics', []))
                for key, value in bball.items():
                    if value is not None:
                        setattr(db_match, key, value)
                # Calculate lead_changes from score_trend
                score_trend = match_data.get('score_trend', [])
                db_match.lead_changes = self._calculate_lead_changes(score_trend)
            # Tennis
            elif sport_id == TENNIS_SPORT_ID:
                tennis = self._extract_tennis_stats(match_data)
                for key, value in tennis.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Volleyball
            elif sport_id == VOLLEYBALL_SPORT_ID:
                volleyball = self._extract_volleyball_stats(match_data)
                for key, value in volleyball.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Hockey
            elif sport_id == HOCKEY_SPORT_ID:
                hockey = self._extract_hockey_stats(match_data)
                for key, value in hockey.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Handball
            elif sport_id == HANDBALL_SPORT_ID:
                handball = self._extract_handball_stats(match_data)
                for key, value in handball.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Baseball
            elif sport_id == BASEBALL_SPORT_ID:
                baseball = self._extract_baseball_stats(match_data)
                for key, value in baseball.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Water Polo
            elif sport_id == WATER_POLO_SPORT_ID:
                water_polo = self._extract_water_polo_stats(match_data)
                for key, value in water_polo.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Table Tennis
            elif sport_id == TABLE_TENNIS_SPORT_ID:
                table_tennis = self._extract_table_tennis_stats(match_data)
                for key, value in table_tennis.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Rugby
            elif sport_id == RUGBY_SPORT_ID:
                rugby = self._extract_rugby_stats(match_data)
                for key, value in rugby.items():
                    if value is not None:
                        setattr(db_match, key, value)
            # Bandy
            elif sport_id == BANDY_SPORT_ID:
                bandy = self._extract_bandy_stats(match_data)
                for key, value in bandy.items():
                    if value is not None:
                        setattr(db_match, key, value)

            self.db.commit()
        except Exception as exc:
            log.warning(f"⚠️ Falha ao buscar detalhes de {platform_id}: {exc}")
            self.db.rollback()

    def _extract_generic_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract generic fields available for all sports from match_data dict."""
        result: Dict[str, Any] = {}

        # Raw arrays
        result['score_trend_raw'] = match_data.get('score_trend') or None
        result['match_statistics_raw'] = match_data.get('statistics') or None
        result['live_events_raw'] = match_data.get('live_events') or None

        # Venue
        venue = match_data.get('venue') or {}
        stadium = venue.get('stadium') or {}
        result['venue_id'] = stadium.get('id') or None

        # Coverage
        result['coverage_level'] = match_data.get('coverage') or None

        # Period metadata
        result['number_of_periods'] = match_data.get('number_of_periods') or None
        result['period_duration'] = match_data.get('period_duration_minutes') or None
        result['leading_team'] = match_data.get('leading_team') or None

        return result

    def _extract_basketball_stats(self, statistics: list) -> Dict[str, Any]:
        """Extract basketball-specific stats from the statistics array.

        Statistics type mapping (period=0 means full game):
            37 = one_pointers (FT)
            38 = two_pointers
            39 = three_pointers
            48 = field_goals
            34 = rebounds
            35 = defensive_rebounds
            36 = offensive_rebounds
            49 = assists
            50 = turnovers
            43 = steals
            26 = shots_blocked
             9 = fouls
            45 = timeouts
            77 = biggest_lead
            78 = team_leads
            79 = time_spent_in_lead
        """
        result: Dict[str, Any] = {}
        if not statistics:
            return result

        # Find period=0 (full game) stats
        full_game_stats = None
        for period_entry in statistics:
            if not isinstance(period_entry, dict):
                continue
            if period_entry.get('period') == 0:
                full_game_stats = period_entry.get('stats', period_entry.get('data', []))
                break

        if not full_game_stats:
            return result

        stat_type_map = {
            37: 'ft',        # free throws
            38: 'fg2',       # 2-point field goals
            39: 'fg3',       # 3-point field goals
            34: 'rebounds',
            49: 'assists',
            50: 'turnovers',
            43: 'steals',
            26: 'blocks',
            9: 'fouls',
            77: 'biggest_lead',
            79: 'time_in_lead',
        }

        for stat in full_game_stats:
            if not isinstance(stat, dict):
                continue
            stat_type = stat.get('type')
            if stat_type not in stat_type_map:
                continue

            team1_raw = stat.get('team1', '')
            team2_raw = stat.get('team2', '')
            name = stat_type_map[stat_type]

            if name in ('ft', 'fg2', 'fg3'):
                made_h, att_h = self._parse_stat_fraction(team1_raw)
                made_a, att_a = self._parse_stat_fraction(team2_raw)
                result[f'{name}_made_home'] = made_h
                result[f'{name}_attempted_home'] = att_h
                result[f'{name}_made_away'] = made_a
                result[f'{name}_attempted_away'] = att_a
            elif name in ('rebounds', 'assists', 'turnovers', 'steals', 'blocks', 'fouls'):
                result[f'{name}_home'] = self._parse_stat_int(team1_raw)
                result[f'{name}_away'] = self._parse_stat_int(team2_raw)
            elif name == 'biggest_lead':
                result['biggest_lead_home'] = self._parse_stat_int(team1_raw)
                result['biggest_lead_away'] = self._parse_stat_int(team2_raw)
            elif name == 'time_in_lead':
                result['time_in_lead_home'] = team1_raw or None
                result['time_in_lead_away'] = team2_raw or None

        return result

    def _extract_tennis_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tennis-specific fields from match data."""
        result: Dict[str, Any] = {}

        # Ground type from competition
        competition = match_data.get('competition') or {}
        result['ground_type'] = competition.get('ground_type') or match_data.get('ground_type') or None

        result['team1_seed'] = match_data.get('team1_seed') or None
        result['team2_seed'] = match_data.get('team2_seed') or None

        # Tournament round - extract first arg string
        tr = match_data.get('tournament_round') or {}
        if isinstance(tr, dict) and tr.get('args'):
            result['tournament_round'] = tr['args'][0]
        elif isinstance(tr, str):
            result['tournament_round'] = tr or None
        else:
            result['tournament_round'] = None

        # Prize money from season
        season = match_data.get('season') or {}
        prize_money = season.get('prize_money') or {}
        prize_currency = season.get('prize_currency') or {}
        result['prize_money'] = prize_money.get('value') if isinstance(prize_money, dict) else None
        result['prize_currency'] = prize_currency.get('value') if isinstance(prize_currency, dict) else None

        # Set durations from period_scores
        period_scores = match_data.get('period_scores') or []
        total_duration = 0
        for ps in period_scores:
            if not isinstance(ps, dict):
                continue
            set_num = ps.get('type', 0)
            duration = ps.get('duration_minutes') or {}
            duration_val = duration.get('value') if isinstance(duration, dict) else None
            if duration_val and 1 <= set_num <= 5:
                result[f'set{set_num}_duration'] = duration_val
                total_duration += duration_val
        result['total_duration'] = total_duration if total_duration > 0 else None

        # Total games from scores type=12
        scores = match_data.get('scores') or []
        for score in scores:
            if isinstance(score, dict) and score.get('type') == 12:
                result['total_games'] = (score.get('team1') or 0) + (score.get('team2') or 0)
                break

        # Statistics - period=0 means match totals
        statistics = match_data.get('statistics') or []
        for stat_period in statistics:
            if not isinstance(stat_period, dict):
                continue
            if stat_period.get('period') != 0:
                continue
            for stat in stat_period.get('data', []):
                if not isinstance(stat, dict):
                    continue
                stat_type = stat.get('type')
                team1_val = str(stat.get('team1', ''))
                team2_val = str(stat.get('team2', ''))

                if stat_type == 11:  # Aces
                    result['aces_home'] = self._parse_stat_int(team1_val)
                    result['aces_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 12:  # Double faults
                    result['double_faults_home'] = self._parse_stat_int(team1_val)
                    result['double_faults_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 33:  # First serve %
                    m1, a1 = self._parse_stat_fraction(team1_val)
                    m2, a2 = self._parse_stat_fraction(team2_val)
                    result['first_serve_pct_home'] = m1 / a1 if a1 is not None and a1 != 0 else None
                    result['first_serve_pct_away'] = m2 / a2 if a2 is not None and a2 != 0 else None
                elif stat_type == 29:  # First serve points won
                    m1, a1 = self._parse_stat_fraction(team1_val)
                    m2, a2 = self._parse_stat_fraction(team2_val)
                    result['first_serve_won_pct_home'] = m1 / a1 if a1 is not None and a1 != 0 else None
                    result['first_serve_won_pct_away'] = m2 / a2 if a2 is not None and a2 != 0 else None
                elif stat_type == 31:  # Second serve points won
                    m1, a1 = self._parse_stat_fraction(team1_val)
                    m2, a2 = self._parse_stat_fraction(team2_val)
                    result['second_serve_won_pct_home'] = m1 / a1 if a1 is not None and a1 != 0 else None
                    result['second_serve_won_pct_away'] = m2 / a2 if a2 is not None and a2 != 0 else None
                elif stat_type == 32:  # Break points won
                    m1, a1 = self._parse_stat_fraction(team1_val)
                    m2, a2 = self._parse_stat_fraction(team2_val)
                    result['break_points_converted_home'] = m1
                    result['break_points_faced_away'] = a1  # BP converted by home = BP faced by away
                    result['break_points_converted_away'] = m2
                    result['break_points_faced_home'] = a2
                    if a1:
                        result['break_points_saved_away'] = a1 - (m1 or 0)
                    if a2:
                        result['break_points_saved_home'] = a2 - (m2 or 0)
                elif stat_type == 19:  # Service games won
                    m1, a1 = self._parse_stat_fraction(team1_val)
                    m2, a2 = self._parse_stat_fraction(team2_val)
                    result['service_games_won_home'] = m1
                    result['service_games_total_home'] = a1
                    result['service_games_won_away'] = m2
                    result['service_games_total_away'] = a2

        # Point by point raw
        result['point_by_point_raw'] = match_data.get('point_by_point') or None

        return result

    def _extract_volleyball_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract volleyball-specific statistics from match data."""
        result: Dict[str, Any] = {}

        scores = match_data.get('scores', [])

        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type == 0:  # Sets won
                result['sets_home'] = team1
                result['sets_away'] = team2
            elif score_type == 1:
                result['set1_home'] = team1
                result['set1_away'] = team2
            elif score_type == 2:
                result['set2_home'] = team1
                result['set2_away'] = team2
            elif score_type == 3:
                result['set3_home'] = team1
                result['set3_away'] = team2
            elif score_type == 4:
                result['set4_home'] = team1
                result['set4_away'] = team2
            elif score_type == 5:
                result['set5_home'] = team1
                result['set5_away'] = team2

        # Calculate totals
        total_home = sum([
            result.get('set1_home', 0) or 0,
            result.get('set2_home', 0) or 0,
            result.get('set3_home', 0) or 0,
            result.get('set4_home', 0) or 0,
            result.get('set5_home', 0) or 0,
        ])
        total_away = sum([
            result.get('set1_away', 0) or 0,
            result.get('set2_away', 0) or 0,
            result.get('set3_away', 0) or 0,
            result.get('set4_away', 0) or 0,
            result.get('set5_away', 0) or 0,
        ])

        result['total_points_home'] = total_home if total_home > 0 else None
        result['total_points_away'] = total_away if total_away > 0 else None

        # Calculate sets played
        sets_played = (result.get('sets_home', 0) or 0) + (result.get('sets_away', 0) or 0)
        result['total_sets_played'] = sets_played if sets_played > 0 else None

        # Average points per set
        if sets_played > 0:
            result['avg_points_per_set_home'] = total_home / sets_played
            result['avg_points_per_set_away'] = total_away / sets_played

        # Point difference per set
        point_diffs = []
        for i in range(1, 6):
            home = result.get(f'set{i}_home')
            away = result.get(f'set{i}_away')
            if home is not None and away is not None and (home > 0 or away > 0):
                point_diffs.append(home - away)
        result['point_diff_per_set'] = point_diffs if point_diffs else None

        return result

    def _extract_hockey_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ice hockey-specific statistics from match data."""
        result: Dict[str, Any] = {}

        # Score by period
        scores = match_data.get('scores', [])
        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type == 1:
                result['period1_home'] = team1
                result['period1_away'] = team2
            elif score_type == 2:
                result['period2_home'] = team1
                result['period2_away'] = team2
            elif score_type == 3:
                result['period3_home'] = team1
                result['period3_away'] = team2
            elif score_type == 4:
                result['overtime_home'] = team1
                result['overtime_away'] = team2
            elif score_type == 5:
                result['shootout_home'] = team1
                result['shootout_away'] = team2

        # Statistics - period=0 means match totals
        statistics = match_data.get('statistics', [])
        for period_stats in statistics:
            if not isinstance(period_stats, dict):
                continue
            if period_stats.get('period') != 0:
                continue

            for stat in period_stats.get('data', []):
                if not isinstance(stat, dict):
                    continue
                stat_type = stat.get('type')
                team1_val = str(stat.get('team1', ''))
                team2_val = str(stat.get('team2', ''))

                if stat_type == 88:  # Puck possession
                    result['puck_possession_home'] = self._parse_percentage(team1_val)
                    result['puck_possession_away'] = self._parse_percentage(team2_val)
                elif stat_type == 1:  # Shots on goal
                    result['shots_on_goal_home'] = self._parse_stat_int(team1_val)
                    result['shots_on_goal_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 84:  # Goals in power play
                    result['power_play_goals_home'] = self._parse_stat_int(team1_val)
                    result['power_play_goals_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 85:  # Goals while short handed
                    result['short_handed_goals_home'] = self._parse_stat_int(team1_val)
                    result['short_handed_goals_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 25:  # Penalties
                    result['penalties_home'] = self._parse_stat_int(team1_val)
                    result['penalties_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 86:  # Penalty minutes
                    result['penalty_minutes_home'] = self._parse_stat_int(team1_val)
                    result['penalty_minutes_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 87:  # Power plays
                    result['power_plays_home'] = self._parse_stat_int(team1_val)
                    result['power_plays_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 90:  # Saves
                    result['saves_home'] = self._parse_stat_int(team1_val)
                    result['saves_away'] = self._parse_stat_int(team2_val)

        # Derived metrics
        shots_home = result.get('shots_on_goal_home') or 0
        shots_away = result.get('shots_on_goal_away') or 0
        saves_home = result.get('saves_home') or 0
        saves_away = result.get('saves_away') or 0
        final_score = next((s for s in scores if isinstance(s, dict) and s.get('type') == 0), None)
        goals_home = final_score.get('team1', 0) if final_score else 0
        goals_away = final_score.get('team2', 0) if final_score else 0

        if saves_home + goals_away > 0:
            result['save_percentage_home'] = saves_home / (saves_home + goals_away)
        if saves_away + goals_home > 0:
            result['save_percentage_away'] = saves_away / (saves_away + goals_home)
        if shots_home > 0:
            result['shooting_percentage_home'] = goals_home / shots_home
        if shots_away > 0:
            result['shooting_percentage_away'] = goals_away / shots_away

        # Goal events with players
        goal_scorers = []
        for event in match_data.get('live_events', []):
            if not isinstance(event, dict):
                continue
            if event.get('type') != 1:  # 1 = Goal
                continue
            goal: Dict[str, Any] = {
                'minute': event.get('minute', {}).get('value') if isinstance(event.get('minute'), dict) else None,
                'team': event.get('position'),
                'score': event.get('main', {}).get('text', {}).get('val') if isinstance(event.get('main'), dict) else None,
            }
            primary = event.get('primary') or {}
            if primary:
                goal['scorer'] = primary.get('text', {}).get('val') if isinstance(primary.get('text'), dict) else None
                player_id = primary.get('player_id') or {}
                goal['scorer_id'] = player_id.get('value') if isinstance(player_id, dict) else None
            secondary = event.get('secondary') or {}
            if secondary and secondary.get('text'):
                goal['assist'] = secondary.get('text', {}).get('val') if isinstance(secondary.get('text'), dict) else None
                assist_id = secondary.get('player_id') or {}
                goal['assist_id'] = assist_id.get('value') if isinstance(assist_id, dict) else None
            goal_scorers.append(goal)

        if goal_scorers:
            result['goal_scorers_raw'] = goal_scorers

        return result

    def _extract_handball_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract handball-specific statistics from match data."""
        result: Dict[str, Any] = {}

        # Score by half
        scores = match_data.get('scores', [])
        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type == 1:
                result['first_half_home'] = team1
                result['first_half_away'] = team2
            elif score_type == 2:
                result['second_half_home'] = team1
                result['second_half_away'] = team2
            elif score_type == 3:
                result['overtime1_home'] = team1
                result['overtime1_away'] = team2
            elif score_type == 4:
                result['overtime2_home'] = team1
                result['overtime2_away'] = team2

        # Statistics - period=0 means match totals
        statistics = match_data.get('statistics', [])
        for period_stats in statistics:
            if not isinstance(period_stats, dict):
                continue
            if period_stats.get('period') != 0:
                continue

            for stat in period_stats.get('data', []):
                if not isinstance(stat, dict):
                    continue
                stat_type = stat.get('type')
                team1_val = str(stat.get('team1', ''))
                team2_val = str(stat.get('team2', ''))

                if stat_type == 1:   # Shots on goal
                    result['shots_on_goal_home'] = self._parse_stat_int(team1_val)
                    result['shots_on_goal_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 2:  # Shots off goal
                    result['shots_off_goal_home'] = self._parse_stat_int(team1_val)
                    result['shots_off_goal_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 7:  # Goalkeeper saves
                    result['goalkeeper_saves_home'] = self._parse_stat_int(team1_val)
                    result['goalkeeper_saves_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 21:  # Red cards
                    result['red_cards_home'] = self._parse_stat_int(team1_val)
                    result['red_cards_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 22:  # Yellow cards
                    result['yellow_cards_home'] = self._parse_stat_int(team1_val)
                    result['yellow_cards_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 25:  # Penalties against (7m suffered)
                    result['penalties_against_home'] = self._parse_stat_int(team1_val)
                    result['penalties_against_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 26:  # Shots blocked
                    result['shots_blocked_home'] = self._parse_stat_int(team1_val)
                    result['shots_blocked_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 40:  # Breakthrough goals
                    result['breakthrough_goals_home'] = self._parse_stat_int(team1_val)
                    result['breakthrough_goals_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 41:  # Fast break goals
                    result['fast_break_goals_home'] = self._parse_stat_int(team1_val)
                    result['fast_break_goals_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 42:  # Pivot goals
                    result['pivot_goals_home'] = self._parse_stat_int(team1_val)
                    result['pivot_goals_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 43:  # Steals
                    result['steals_home'] = self._parse_stat_int(team1_val)
                    result['steals_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 44:  # Suspension minutes
                    result['suspension_minutes_home'] = self._parse_stat_int(team1_val)
                    result['suspension_minutes_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 45:  # Timeouts
                    result['timeouts_home'] = self._parse_stat_int(team1_val)
                    result['timeouts_away'] = self._parse_stat_int(team2_val)
                elif stat_type == 52:  # Suspensions count
                    result['suspensions_home'] = self._parse_stat_int(team1_val)
                    result['suspensions_away'] = self._parse_stat_int(team2_val)

        # Derived metrics
        shots_home = result.get('shots_on_goal_home') or 0
        shots_away = result.get('shots_on_goal_away') or 0
        saves_home = result.get('goalkeeper_saves_home') or 0
        saves_away = result.get('goalkeeper_saves_away') or 0
        final_score = next((s for s in scores if isinstance(s, dict) and s.get('type') == 0), None)
        goals_home = final_score.get('team1', 0) if final_score else 0
        goals_away = final_score.get('team2', 0) if final_score else 0

        if saves_home + goals_away > 0:
            result['save_percentage_home'] = saves_home / (saves_home + goals_away)
        if saves_away + goals_home > 0:
            result['save_percentage_away'] = saves_away / (saves_away + goals_home)
        if shots_home > 0:
            result['shooting_percentage_home'] = goals_home / shots_home
        if shots_away > 0:
            result['shooting_percentage_away'] = goals_away / shots_away

        # Goals per half
        goals_per_half_home = [result.get('first_half_home'), result.get('second_half_home')]
        goals_per_half_away = [result.get('first_half_away'), result.get('second_half_away')]
        if any(v is not None for v in goals_per_half_home):
            result['goals_per_half_home'] = goals_per_half_home
        if any(v is not None for v in goals_per_half_away):
            result['goals_per_half_away'] = goals_per_half_away

        # Goal events with players; count 7m penalty goals
        goal_scorers = []
        penalty_goals_home = 0
        penalty_goals_away = 0

        for event in match_data.get('live_events', []):
            if not isinstance(event, dict):
                continue
            if event.get('type') != 1:  # 1 = Goal
                continue
            subtype = event.get('subtype')
            position = event.get('position')

            if subtype == 11:  # 7m penalty goal
                if position == 1:
                    penalty_goals_home += 1
                else:
                    penalty_goals_away += 1

            goal: Dict[str, Any] = {
                'minute': event.get('minute', {}).get('value') if isinstance(event.get('minute'), dict) else None,
                'team': position,
                'is_penalty': subtype == 11,
                'score': event.get('main', {}).get('text', {}).get('val') if isinstance(event.get('main'), dict) else None,
            }
            primary = event.get('primary') or {}
            if primary:
                goal['scorer'] = primary.get('text', {}).get('val') if isinstance(primary.get('text'), dict) else None
                player_id = primary.get('player_id') or {}
                goal['scorer_id'] = player_id.get('value') if isinstance(player_id, dict) else None
            secondary = event.get('secondary') or {}
            if secondary and secondary.get('text') and not secondary.get('text', {}).get('args'):
                goal['assist'] = secondary.get('text', {}).get('val') if isinstance(secondary.get('text'), dict) else None
                assist_id = secondary.get('player_id') or {}
                goal['assist_id'] = assist_id.get('value') if isinstance(assist_id, dict) else None
            goal_scorers.append(goal)

        if penalty_goals_home > 0:
            result['penalty_goals_home'] = penalty_goals_home
        if penalty_goals_away > 0:
            result['penalty_goals_away'] = penalty_goals_away
        if goal_scorers:
            result['goal_scorers_raw'] = goal_scorers

        return result

    def _extract_baseball_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract baseball-specific statistics from match data."""
        result: Dict[str, Any] = {}

        scores = match_data.get('scores', [])

        # Score type to inning field mapping
        # Types 1-5 = Innings 1-5, Types 13-16 = Innings 6-9, Types 17+ = Extra innings
        inning_map = {
            1:  ('inning1_home', 'inning1_away'),
            2:  ('inning2_home', 'inning2_away'),
            3:  ('inning3_home', 'inning3_away'),
            4:  ('inning4_home', 'inning4_away'),
            5:  ('inning5_home', 'inning5_away'),
            13: ('inning6_home', 'inning6_away'),
            14: ('inning7_home', 'inning7_away'),
            15: ('inning8_home', 'inning8_away'),
            16: ('inning9_home', 'inning9_away'),
        }

        extra_innings_home: list = []
        extra_innings_away: list = []

        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type in inning_map:
                home_key, away_key = inning_map[score_type]
                result[home_key] = team1
                result[away_key] = team2
            elif score_type is not None and score_type >= 17:  # Extra innings
                extra_innings_home.append(team1)
                extra_innings_away.append(team2)

        if extra_innings_home:
            result['extra_innings_home'] = extra_innings_home
            result['extra_innings_away'] = extra_innings_away

        # Calculate totals
        innings_home = [
            result.get('inning1_home') or 0,
            result.get('inning2_home') or 0,
            result.get('inning3_home') or 0,
            result.get('inning4_home') or 0,
            result.get('inning5_home') or 0,
            result.get('inning6_home') or 0,
            result.get('inning7_home') or 0,
            result.get('inning8_home') or 0,
            result.get('inning9_home') or 0,
        ]
        innings_away = [
            result.get('inning1_away') or 0,
            result.get('inning2_away') or 0,
            result.get('inning3_away') or 0,
            result.get('inning4_away') or 0,
            result.get('inning5_away') or 0,
            result.get('inning6_away') or 0,
            result.get('inning7_away') or 0,
            result.get('inning8_away') or 0,
            result.get('inning9_away') or 0,
        ]

        total_home = sum(innings_home) + sum(extra_innings_home)
        total_away = sum(innings_away) + sum(extra_innings_away)

        # Store totals unconditionally (0 is valid for shutout games)
        result['total_runs_home'] = total_home
        result['total_runs_away'] = total_away

        # Total innings played
        innings_played = 9 + len(extra_innings_home)
        result['total_innings_played'] = innings_played

        # Average runs per inning
        if innings_played > 0:
            result['runs_per_inning_home'] = round(total_home / innings_played, 2)
            result['runs_per_inning_away'] = round(total_away / innings_played, 2)

        # First 5 innings (F5 betting) - only set when we have at least some inning data
        has_inning_data = any(
            result.get(f'inning{i}_home') is not None for i in range(1, 6)
        )
        if has_inning_data:
            result['first_5_innings_home'] = sum(innings_home[:5])
            result['first_5_innings_away'] = sum(innings_away[:5])

        # Last 4 innings (innings 6-9 only, extra innings tracked separately)
        result['last_4_innings_home'] = sum(innings_home[5:9])
        result['last_4_innings_away'] = sum(innings_away[5:9])

        return result

    def _extract_water_polo_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract water polo-specific statistics from match data (4 quarters)."""
        result: Dict[str, Any] = {}
        scores = match_data.get('scores', [])

        quarter_map = {
            1: ('wp_quarter1_home', 'wp_quarter1_away'),
            2: ('wp_quarter2_home', 'wp_quarter2_away'),
            3: ('wp_quarter3_home', 'wp_quarter3_away'),
            4: ('wp_quarter4_home', 'wp_quarter4_away'),
        }

        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type in quarter_map:
                home_key, away_key = quarter_map[score_type]
                result[home_key] = team1
                result[away_key] = team2

        # Calculate half totals
        q1h = result.get('wp_quarter1_home', 0) or 0
        q2h = result.get('wp_quarter2_home', 0) or 0
        q3h = result.get('wp_quarter3_home', 0) or 0
        q4h = result.get('wp_quarter4_home', 0) or 0
        q1a = result.get('wp_quarter1_away', 0) or 0
        q2a = result.get('wp_quarter2_away', 0) or 0
        q3a = result.get('wp_quarter3_away', 0) or 0
        q4a = result.get('wp_quarter4_away', 0) or 0

        result['wp_first_half_home'] = q1h + q2h
        result['wp_first_half_away'] = q1a + q2a
        result['wp_second_half_home'] = q3h + q4h
        result['wp_second_half_away'] = q3a + q4a

        total_home = q1h + q2h + q3h + q4h
        total_away = q1a + q2a + q3a + q4a

        result['wp_total_goals_home'] = total_home if total_home > 0 else None
        result['wp_total_goals_away'] = total_away if total_away > 0 else None

        if total_home > 0:
            result['wp_goals_per_quarter_home'] = round(total_home / 4, 2)
        if total_away > 0:
            result['wp_goals_per_quarter_away'] = round(total_away / 4, 2)

        return result

    def _extract_table_tennis_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract table tennis-specific statistics from match data (up to 7 sets)."""
        result: Dict[str, Any] = {}
        scores = match_data.get('scores', [])

        set_map = {
            1: ('tt_set1_home', 'tt_set1_away'),
            2: ('tt_set2_home', 'tt_set2_away'),
            3: ('tt_set3_home', 'tt_set3_away'),
            4: ('tt_set4_home', 'tt_set4_away'),
            5: ('tt_set5_home', 'tt_set5_away'),
            6: ('tt_set6_home', 'tt_set6_away'),
            7: ('tt_set7_home', 'tt_set7_away'),
        }

        close_sets = 0
        deuce_sets = 0

        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type == 0:  # Sets won
                result['tt_sets_home'] = team1
                result['tt_sets_away'] = team2
            elif score_type in set_map:
                home_key, away_key = set_map[score_type]
                result[home_key] = team1
                result[away_key] = team2

                # Track deuce sets (both reached 10+) and close sets (deuce ended by 2 pts)
                if team1 >= 10 and team2 >= 10:
                    deuce_sets += 1
                    if abs(team1 - team2) == 2:
                        close_sets += 1

        # Calculate totals
        total_home = sum(result.get(f'tt_set{i}_home', 0) or 0 for i in range(1, 8))
        total_away = sum(result.get(f'tt_set{i}_away', 0) or 0 for i in range(1, 8))

        result['tt_total_points_home'] = total_home if total_home > 0 else None
        result['tt_total_points_away'] = total_away if total_away > 0 else None

        sets_played = (result.get('tt_sets_home', 0) or 0) + (result.get('tt_sets_away', 0) or 0)
        result['tt_total_sets_played'] = sets_played if sets_played > 0 else None

        if sets_played > 0:
            result['tt_avg_points_per_set_home'] = round(total_home / sets_played, 2)
            result['tt_avg_points_per_set_away'] = round(total_away / sets_played, 2)

        result['tt_close_sets'] = close_sets if close_sets > 0 else None
        result['tt_deuce_sets'] = deuce_sets if deuce_sets > 0 else None

        return result

    def _extract_rugby_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract rugby-specific statistics from match data (2 halves of 40 min)."""
        result: Dict[str, Any] = {}
        scores = match_data.get('scores', [])

        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type == 0:  # Final
                result['rugby_total_points_home'] = team1
                result['rugby_total_points_away'] = team2
            elif score_type == 1:  # 1st half
                result['rugby_first_half_home'] = team1
                result['rugby_first_half_away'] = team2
            elif score_type == 2:  # 2nd half
                result['rugby_second_half_home'] = team1
                result['rugby_second_half_away'] = team2

        # Calculate derived metrics
        h1_home = result.get('rugby_first_half_home', 0) or 0
        h1_away = result.get('rugby_first_half_away', 0) or 0
        h2_home = result.get('rugby_second_half_home', 0) or 0
        h2_away = result.get('rugby_second_half_away', 0) or 0
        total_home = result.get('rugby_total_points_home', 0) or 0
        total_away = result.get('rugby_total_points_away', 0) or 0

        result['rugby_first_half_margin'] = h1_home - h1_away
        result['rugby_second_half_margin'] = h2_home - h2_away

        # Detect comeback (losing at HT, won at FT)
        ht_leader = 1 if h1_home > h1_away else (2 if h1_away > h1_home else 0)
        ft_leader = 1 if total_home > total_away else (2 if total_away > total_home else 0)
        result['rugby_comeback'] = (ht_leader != 0 and ft_leader != 0 and ht_leader != ft_leader)

        if h1_home + h2_home > 0:
            result['rugby_points_per_half_home'] = round((h1_home + h2_home) / 2, 2)
        if h1_away + h2_away > 0:
            result['rugby_points_per_half_away'] = round((h1_away + h2_away) / 2, 2)

        return result

    def _extract_bandy_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract bandy-specific statistics from match data (2 halves of 45 min)."""
        result: Dict[str, Any] = {}
        scores = match_data.get('scores', [])

        for score in scores:
            if not isinstance(score, dict):
                continue
            score_type = score.get('type')
            team1 = score.get('team1', 0)
            team2 = score.get('team2', 0)

            if score_type == 0:  # Final
                result['bandy_total_goals_home'] = team1
                result['bandy_total_goals_away'] = team2
            elif score_type == 1:  # 1st half
                result['bandy_first_half_home'] = team1
                result['bandy_first_half_away'] = team2
            elif score_type == 2:  # 2nd half
                result['bandy_second_half_home'] = team1
                result['bandy_second_half_away'] = team2

        # Calculate derived metrics
        h1_home = result.get('bandy_first_half_home', 0) or 0
        h1_away = result.get('bandy_first_half_away', 0) or 0
        h2_home = result.get('bandy_second_half_home', 0) or 0
        h2_away = result.get('bandy_second_half_away', 0) or 0
        total_home = result.get('bandy_total_goals_home', 0) or 0
        total_away = result.get('bandy_total_goals_away', 0) or 0

        result['bandy_first_half_margin'] = h1_home - h1_away
        result['bandy_second_half_margin'] = h2_home - h2_away

        # Detect comeback (losing at HT, won at FT)
        ht_leader = 1 if h1_home > h1_away else (2 if h1_away > h1_home else 0)
        ft_leader = 1 if total_home > total_away else (2 if total_away > total_home else 0)
        result['bandy_comeback'] = (ht_leader != 0 and ft_leader != 0 and ht_leader != ft_leader)

        if h1_home + h2_home > 0:
            result['bandy_goals_per_half_home'] = round((h1_home + h2_home) / 2, 2)
        if h1_away + h2_away > 0:
            result['bandy_goals_per_half_away'] = round((h1_away + h2_away) / 2, 2)

        return result

    @staticmethod
    def _parse_percentage(value: str) -> Optional[float]:
        """Parse a percentage string like '56%' into a float like 0.56."""
        if not value:
            return None
        m = re.match(r'(\d+(?:\.\d+)?)\s*%', str(value).strip())
        if m:
            return float(m.group(1)) / 100.0
        try:
            return float(str(value).strip()) / 100.0
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_stat_fraction(value: str):
        """Parse '11/12 (92%)' -> (11, 12). Returns (None, None) on failure."""
        if not value:
            return None, None
        # Try "made/attempted" pattern
        m = re.match(r'(\d+)\s*/\s*(\d+)', str(value).strip())
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    @staticmethod
    def _parse_stat_int(value) -> Optional[int]:
        """Parse an integer stat value, returning None on failure."""
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _calculate_lead_changes(score_trend: list) -> Optional[int]:
        """Count lead changes from score_trend list.

        A lead change occurs when the sign of 'diff' flips between entries
        (excluding ties where diff == 0).
        """
        if not score_trend:
            return None
        changes = 0
        prev_sign = None
        for entry in score_trend:
            if not isinstance(entry, dict):
                continue
            diff = entry.get('diff', 0)
            if diff == 0:
                continue
            sign = 1 if diff > 0 else -1
            if prev_sign is not None and sign != prev_sign:
                changes += 1
            prev_sign = sign
        return changes

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

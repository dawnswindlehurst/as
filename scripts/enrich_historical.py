"""Script to enrich historical matches with V2 API data (xG, player stats, detailed events)."""
import asyncio
import argparse
from datetime import datetime, timezone
from collections import Counter
from typing import List, Optional, Dict, Any, Set, Tuple
from database.db import get_db_session
from database.scorealarm_models import ScorealarmMatch
from scrapers.superbet.scorealarm_client import ScorealarmClient
from utils.gentle_rate_limiter import GentleRateLimiter
from utils.logger import log


# Focus V2 enrichment only where we have confirmed/expected useful extra payloads.
DEFAULT_ENRICH_SPORT_IDS = {55, 57}  # Futebol, Tênis
FOOTBALL_SPORT_ID = 55
TENNIS_SPORT_ID = 57
ALLOWED_V2_SPORT_IDS = {FOOTBALL_SPORT_ID, TENNIS_SPORT_ID}


class EnrichHistoricalJob:
    """Enriches historical matches with V2 API data."""
    
    def __init__(
        self,
        limit: Optional[int] = None,
        force: bool = False,
        delay: int = 100,
        sport_ids: Optional[Set[int]] = None,
        all_sports: bool = False,
        inspect_fields: bool = False,
    ):
        """
        Initialize enrichment job.
        
        Args:
            limit: Maximum number of matches to enrich (None = all pending)
            force: Force re-enrichment of already enriched matches
            delay: Delay between requests in milliseconds
            sport_ids: Optional set of sport IDs to enrich
            all_sports: Enrich all sports (disables sport_ids filter)
            inspect_fields: Log aggregate field/type discovery from V2 payloads
        """
        self.scorealarm_client = ScorealarmClient()
        self.limiter = GentleRateLimiter(
            requests_per_minute=10,
            delay_between_requests=delay / 1000.0,  # Convert ms to seconds
            delay_between_sports=5,  # Shorter delay for same API
            delay_between_tournaments=2,
            night_mode_speedup=True
        )
        self.db = get_db_session()
        self.limit = limit
        self.force = force
        self.all_sports = all_sports
        if self.all_sports:
            log.warning("⚠️ --all-sports ignorado: V2 suportado apenas para futebol (55) e tênis (57)")
        self.inspect_fields = inspect_fields
        requested_sport_ids = set(sport_ids or DEFAULT_ENRICH_SPORT_IDS)
        self.sport_ids = requested_sport_ids.intersection(ALLOWED_V2_SPORT_IDS)
        ignored_sports = sorted(requested_sport_ids - ALLOWED_V2_SPORT_IDS)
        if ignored_sports:
            log.warning(f"⚠️ Ignorando sport_ids sem suporte V2: {ignored_sports}")

        # Field discovery tracking (useful when mapping sports like tennis)
        self.match_stat_types: Counter[Tuple[int, str]] = Counter()
        self.live_event_types: Counter[Tuple[int, Optional[int]]] = Counter()
        self.matches_with_stats = 0
        self.matches_with_events = 0
        
        # Stats tracking
        self.stats = {
            "total": 0,
            "enriched": 0,
            "no_data": 0,
            "errors": 0,
            "parse_errors": 0,
            "skipped": 0
        }
    
    async def run(self):
        """Execute enrichment."""
        log.info("="*60)
        log.info("🔍 ENRIQUECIMENTO DE PARTIDAS HISTÓRICAS - V2 API")
        log.info("="*60)
        
        try:
            # Get matches to enrich
            matches = self._get_matches_to_enrich()
            
            if not matches:
                log.info("✅ Nenhuma partida pendente de enriquecimento")
                return
            
            self.stats["total"] = len(matches)
            log.info(f"📊 {self.stats['total']} partidas para enriquecer")
            
            # Process in batches
            batch_size = 100
            total_batches = (len(matches) + batch_size - 1) // batch_size
            
            log.info(f"🚀 Iniciando enriquecimento em batches de {batch_size}...")
            
            async with self.scorealarm_client as scorealarm:
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(matches))
                    batch = matches[start_idx:end_idx]
                    
                    log.info(f"\n📦 Batch {batch_num + 1}/{total_batches}: {len(batch)} partidas")
                    
                    for i, match in enumerate(batch):
                        try:
                            await self._enrich_match(match, scorealarm)
                            
                            # Progress log every 10 matches
                            if (i + 1) % 10 == 0:
                                log.info(f"  📈 {i + 1}/{len(batch)} partidas processadas no batch")
                            
                            # Rate limiting
                            await self.limiter.wait()
                            
                        except Exception as e:
                            self.stats["errors"] += 1
                            log.error(f"  ❌ Erro na partida {match.id}: {e}")
                            continue
                    
                    log.info(f"✅ Batch {batch_num + 1}/{total_batches}: {len(batch)} partidas processadas")
                    
                    # Commit batch
                    try:
                        self.db.commit()
                        log.info(f"💾 Batch {batch_num + 1} salvo no banco")
                    except Exception as e:
                        log.error(f"❌ Erro ao salvar batch {batch_num + 1}: {e}")
                        self.db.rollback()
            
            # Final summary
            log.info("\n" + "="*60)
            log.info("🎉 ENRIQUECIMENTO CONCLUÍDO")
            log.info("="*60)
            log.info(f"📊 Total: {self.stats['total']} partidas")
            if self.stats['total'] > 0:
                log.info(f"✅ Enriquecidas: {self.stats['enriched']} ({self.stats['enriched']/self.stats['total']*100:.1f}%)")
                log.info(f"⚠️ Sem dados V2: {self.stats['no_data']} ({self.stats['no_data']/self.stats['total']*100:.1f}%)")
                log.info(f"❌ Erros: {self.stats['errors']} ({self.stats['errors']/self.stats['total']*100:.1f}%)")
                log.info(f"⚠️ Parse errors: {self.stats['parse_errors']} ({self.stats['parse_errors']/self.stats['total']*100:.1f}%)")
            else:
                log.info(f"✅ Enriquecidas: {self.stats['enriched']}")
                log.info(f"⚠️ Sem dados V2: {self.stats['no_data']}")
                log.info(f"❌ Erros: {self.stats['errors']}")
                log.info(f"⚠️ Parse errors: {self.stats['parse_errors']}")
            log.info(f"⏭️ Puladas: {self.stats['skipped']}")
            if self.inspect_fields:
                self._log_field_discovery_summary()
            log.info("="*60)
            
        except Exception as e:
            log.error(f"❌ Erro fatal no enriquecimento: {e}")
            raise
    
    def _get_matches_to_enrich(self) -> List[ScorealarmMatch]:
        """
        Get matches that need enrichment.
        
        Returns:
            List of matches to enrich
        """
        log.info("🔍 Buscando partidas para enriquecer...")
        
        query = self.db.query(ScorealarmMatch)
        
        # Filter criteria
        if not self.force:
            # Only matches not yet enriched
            query = query.filter(ScorealarmMatch.enriched_at.is_(None))
        
        # Only finished matches with an offer_id (needed for V2 API)
        query = query.filter(
            ScorealarmMatch.is_finished == True,
            ScorealarmMatch.offer_id.isnot(None)
        )
        
        # Apply sport filter (V2 only supported for football + tennis)
        query = query.filter(ScorealarmMatch.sport_id.in_(self.sport_ids))

        # Apply limit if specified
        if self.limit:
            query = query.limit(self.limit)
        
        matches = query.all()
        
        total_matches = self.db.query(ScorealarmMatch).filter(
            ScorealarmMatch.is_finished == True
        ).count()
        
        scope_desc = f"sport_ids={sorted(self.sport_ids)}"
        log.info(f"📊 {len(matches)} partidas pendentes de {total_matches} total ({scope_desc})")
        
        return matches
    
    async def _enrich_match(self, match: ScorealarmMatch, scorealarm: ScorealarmClient):
        """
        Enrich a single match with V2 API data.
        
        Args:
            match: Match to enrich
            scorealarm: Scorealarm client instance
        """
        # Extract fixture_id from offer_id (e.g., "ax:match:12001839" -> "12001839")
        fixture_id = match.offer_id
        if not fixture_id:
            self.stats["skipped"] += 1
            return
        
        # Get fixture stats from V2 API
        sport_hint = None
        if match.sport_id == 55:
            sport_hint = "soccer"
        elif match.sport_id == 57:
            sport_hint = "tennis"

        fixture_stats = await scorealarm.get_fixture_stats(fixture_id, sport_hint=sport_hint)
        
        if not fixture_stats:
            self.stats["no_data"] += 1
            log.warning(f"  ⚠️ Partida {match.id}: sem dados V2 disponíveis")
            # Mark as enriched even without data to avoid reprocessing
            match.enriched_at = datetime.now(timezone.utc)
            return
        
        match_stats = fixture_stats.match_stats or []
        live_events = fixture_stats.live_events or []

        if self.inspect_fields:
            self._capture_field_discovery(match_stats, live_events)

        # Save ALL raw match_stats data
        if match_stats:
            match.match_stats_raw = [
                {
                    "type": s.type,
                    "team1": s.team1,
                    "team2": s.team2,
                    "stat_name": s.stat_name
                }
                for s in match_stats
            ]

        # Save ALL raw live_events data
        if live_events:
            match.live_events_raw = [
                {
                    "type": e.type,
                    "subtype": e.subtype,
                    "minute": e.minute,
                    "added_time": e.added_time,
                    "side": e.side,
                    "player_id": e.player_id,
                    "player_name": e.player_name,
                    "secondary_player_id": e.secondary_player_id,
                    "secondary_player_name": e.secondary_player_name,
                    "score": e.score
                }
                for e in live_events
            ]

        if match.sport_id == TENNIS_SPORT_ID:
            self._extract_tennis_stats(match, fixture_stats)

        try:
            if match.sport_id == FOOTBALL_SPORT_ID:
                self._extract_football_stats(match, match_stats, live_events)
        except Exception as parse_error:
            self.stats["parse_errors"] += 1
            log.warning(f"  ⚠️ Partida {match.id}: erro ao parsear campos enriquecidos: {parse_error}")

        # Mark as enriched
        match.enriched_at = datetime.now(timezone.utc)
        self.stats["enriched"] += 1

    def _extract_football_stats(self, match: ScorealarmMatch, match_stats: List[Any], live_events: List[Any]):
        """Extract football-specific enrichment fields."""
        # Extract xG (type=19)
        xg_stats = [s for s in match_stats if s.type == 19]
        if xg_stats:
            xg_stat = xg_stats[0]
            try:
                match.xg_home = float(xg_stat.team1) if xg_stat.team1 else None
                match.xg_away = float(xg_stat.team2) if xg_stat.team2 else None
            except (ValueError, TypeError):
                match.xg_home = None
                match.xg_away = None

        # Extract shots on goal (type=2)
        shots_stats = [s for s in match_stats if s.type == 2]
        if shots_stats:
            shots_stat = shots_stats[0]
            try:
                match.shots_on_goal_home = int(shots_stat.team1) if shots_stat.team1 else None
                match.shots_on_goal_away = int(shots_stat.team2) if shots_stat.team2 else None
            except (ValueError, TypeError):
                match.shots_on_goal_home = None
                match.shots_on_goal_away = None

        # Extract corners (type=5)
        corner_stats = [s for s in match_stats if s.type == 5]
        if corner_stats:
            corner_stat = corner_stats[0]
            try:
                match.corners_home = int(corner_stat.team1) if corner_stat.team1 else None
                match.corners_away = int(corner_stat.team2) if corner_stat.team2 else None
            except (ValueError, TypeError):
                match.corners_home = None
                match.corners_away = None

        # Extract goal events (type=4)
        goal_events = [e for e in live_events if e.type == 4]
        if goal_events:
            goals_data = []
            for goal in goal_events:
                goal_dict = {
                    "minute": goal.minute,
                    "added_time": goal.added_time,
                    "player_id": goal.player_id,
                    "player_name": goal.player_name,
                    "assist_player_id": goal.secondary_player_id,
                    "assist_player_name": goal.secondary_player_name,
                    "side": goal.side,  # 1=home, 2=away
                    "score": goal.score
                }
                goals_data.append(goal_dict)

            match.goal_events = goals_data

    def _extract_tennis_stats(self, match: ScorealarmMatch, fixture_stats: Any):
        """Extract tennis-focused metrics from V2 payload into DB JSON columns."""
        type_to_key = {
            11: "aces",
            12: "double_faults",
            15: "max_points_in_row",
            16: "max_games_in_row",
            17: "service_points_won",
            19: "service_games_won",
            29: "first_serve_points_won",
            31: "second_serve_points_won",
            32: "break_points_won",
            33: "first_serve_percentage",
            46: "second_serve_percentage",
        }

        def serialize_stat(stat: Any) -> Dict[str, Any]:
            return {
                "type": stat.type,
                "key": type_to_key.get(stat.type),
                "stat_name": stat.stat_name,
                "team1": stat.team1,
                "team2": stat.team2,
            }

        totals = [serialize_stat(stat) for stat in (fixture_stats.match_stats or []) if stat.type in type_to_key]
        periods = {}
        for period, stats in (fixture_stats.statistics_by_period or {}).items():
            periods[str(period)] = [serialize_stat(stat) for stat in stats if stat.type in type_to_key]

        match.tennis_match_metrics = totals or None
        match.tennis_period_metrics = periods or None

    def _capture_field_discovery(self, match_stats: List[Any], live_events: List[Any]):
        """Capture aggregate type/subtype information from payloads."""
        if match_stats:
            self.matches_with_stats += 1
            for stat in match_stats:
                self.match_stat_types[(stat.type, stat.stat_name or "")] += 1

        if live_events:
            self.matches_with_events += 1
            for event in live_events:
                self.live_event_types[(event.type, event.subtype)] += 1

    def _log_field_discovery_summary(self):
        """Log consolidated field discovery details for quick API exploration."""
        log.info("\n🧪 RESUMO DE CAMPOS V2 OBSERVADOS")
        log.info(
            f"Partidas com match_stats: {self.matches_with_stats} | "
            f"partidas com live_events: {self.matches_with_events}"
        )

        if self.match_stat_types:
            log.info("📌 match_stats observados (type, stat_name, ocorrências):")
            for (stat_type, stat_name), count in self.match_stat_types.most_common():
                label = stat_name or "<sem nome>"
                log.info(f"  - ({stat_type}, {label}): {count}")
        else:
            log.info("📌 match_stats observados: nenhum")

        if self.live_event_types:
            log.info("📌 live_events observados (type, subtype, ocorrências):")
            for (event_type, event_subtype), count in self.live_event_types.most_common():
                log.info(f"  - ({event_type}, {event_subtype}): {count}")
        else:
            log.info("📌 live_events observados: nenhum")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enrich historical matches with V2 API data (xG, player events, detailed stats)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of matches to enrich (default: all pending)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-enrichment of already enriched matches"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=100,
        help="Delay between requests in milliseconds (default: 100)"
    )
    parser.add_argument(
        "--sport-ids",
        type=str,
        default="55,57",
        help="Comma-separated sport IDs to enrich (default: 55,57 -> Futebol,Tênis)",
    )
    parser.add_argument(
        "--all-sports",
        action="store_true",
        help="[LEGADO] ignorado: V2 só para 55 (futebol) e 57 (tênis)",
    )
    parser.add_argument(
        "--inspect-fields",
        action="store_true",
        help="Log aggregate match_stats/live_events types to inspect API payload fields",
    )
    
    args, unknown_args = parser.parse_known_args()
    if unknown_args:
        log.warning(f"⚠️ Ignorando argumentos não reconhecidos: {' '.join(unknown_args)}")
    
    sport_ids = {
        int(part.strip())
        for part in args.sport_ids.split(",")
        if part.strip()
    }

    job = EnrichHistoricalJob(
        limit=args.limit,
        force=args.force,
        delay=args.delay,
        sport_ids=sport_ids,
        all_sports=args.all_sports,
        inspect_fields=args.inspect_fields,
    )
    
    await job.run()


if __name__ == "__main__":
    asyncio.run(main())

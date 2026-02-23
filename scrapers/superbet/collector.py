"""
Complete odds collector for all sports from Superbet.
"""
import asyncio
import logging
from datetime import datetime
from typing import List
from dataclasses import dataclass

from .superbet_client import SuperbetClient
from .odds_tracker import OddsTracker
from .sport_mapping import (
    SUPERBET_SPORTS, 
    ALL_SPORTS, 
    supports_player_props,
    get_sport_name
)

logger = logging.getLogger(__name__)


@dataclass
class CollectionStats:
    """Statistics from a collection run."""
    sport_id: int
    sport_name: str
    events_found: int
    events_with_odds: int
    total_markets: int
    player_props: int
    odds_changes: int
    line_changes: int
    errors: int
    duration_seconds: float


class SuperbetCollector:
    """Collects odds from all sports on Superbet."""
    
    def __init__(
        self,
        sports: List[int] = None,
        storage_dir: str = "data/odds_history",
        delay_between_events: float = 0.5,  # Delay entre eventos
        delay_between_sports: float = 2.0,  # Delay entre esportes
    ):
        self.sports = sports or ALL_SPORTS
        self.tracker = OddsTracker(storage_dir)
        self.stats: List[CollectionStats] = []
        self.delay_between_events = delay_between_events
        self.delay_between_sports = delay_between_sports
    
    async def collect_sport(
        self, 
        client: SuperbetClient, 
        sport_id: int,
        full_odds: bool = True
    ) -> CollectionStats:
        """Collect all events for a sport."""
        sport_name = get_sport_name(sport_id)
        start_time = datetime.now()
        
        stats = CollectionStats(
            sport_id=sport_id,
            sport_name=sport_name,
            events_found=0,
            events_with_odds=0,
            total_markets=0,
            player_props=0,
            odds_changes=0,
            line_changes=0,
            errors=0,
            duration_seconds=0,
        )
        
        try:
            # Buscar lista de eventos
            events = await client.get_events_by_sport(sport_id)
            
            if not events:
                return stats
            
            stats.events_found = len(events)
            
            # Para cada evento, buscar odds completas
            for i, event in enumerate(events):
                try:
                    event_to_process = event
                    
                    # Buscar full odds
                    if full_odds and event.event_id:
                        try:
                            full_event = await client.get_event_full_odds(int(event.event_id))
                            if full_event and full_event.markets:
                                event_to_process = full_event
                        except Exception as e:
                            logger.debug(f"Could not get full odds: {e}")
                        
                        # Delay entre eventos para evitar rate limit
                        if self.delay_between_events > 0 and i < len(events) - 1:
                            await asyncio.sleep(self.delay_between_events)
                    
                    if not event_to_process.markets:
                        continue
                    
                    stats.events_with_odds += 1
                    stats.total_markets += len(event_to_process.markets)
                    
                    event_name = f"{event_to_process.team1} vs {event_to_process.team2}"
                    event_date = str(event_to_process.start_time.date()) if event_to_process.start_time else ""
                    event_id = str(event_to_process.event_id) if event_to_process.event_id else ""
                    
                    if not event_id:
                        continue
                    
                    # Carregar histórico existente
                    self.tracker.load_event(event_id)
                    
                    # Processar mercados de jogador
                    if supports_player_props(sport_id):
                        for market in event_to_process.markets:
                            is_player_prop = 'Jogador -' in market.market_name
                            
                            if is_player_prop:
                                stats.player_props += 1
                                prop_type = market.market_name.replace('Jogador - ', '').split(' (')[0]
                                
                                players_processed = set()
                                for odd in market.odds_list:
                                    parts = odd.outcome_name.split(' - ')
                                    if len(parts) >= 2:
                                        player = parts[0]
                                        line_part = parts[1]
                                        
                                        if player in players_processed:
                                            continue
                                        
                                        if 'Mais de' in line_part:
                                            try:
                                                line = float(line_part.split('Mais de ')[1].split()[0])
                                                over_odds = odd.odds
                                                
                                                under_odds = over_odds
                                                for o2 in market.odds_list:
                                                    if player in o2.outcome_name and 'Menos de' in o2.outcome_name:
                                                        under_odds = o2.odds
                                                        break
                                                
                                                result = self.tracker.update_prop(
                                                    event_id=event_id,
                                                    event_name=event_name,
                                                    event_date=event_date,
                                                    player_name=player,
                                                    prop_type=prop_type,
                                                    line=line,
                                                    odds_over=over_odds,
                                                    odds_under=under_odds,
                                                )
                                                
                                                if result['odds_changed']:
                                                    stats.odds_changes += 1
                                                if result['line_changed']:
                                                    stats.line_changes += 1
                                                
                                                players_processed.add(player)
                                            except (ValueError, IndexError):
                                                pass
                    
                    self.tracker.save_event(event_id)
                    
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    stats.errors += 1
            
        except Exception as e:
            logger.error(f"[{sport_name}] Collection error: {e}")
            stats.errors += 1
        
        stats.duration_seconds = (datetime.now() - start_time).total_seconds()
        return stats
    
    async def collect_all(self, full_odds: bool = True) -> List[CollectionStats]:
        """Collect from all configured sports."""
        start_time = datetime.now()
        self.stats = []
        
        async with SuperbetClient() as client:
            for i, sport_id in enumerate(self.sports):
                stats = await self.collect_sport(client, sport_id, full_odds)
                self.stats.append(stats)
                if stats.events_found > 0:
                    props = f", {stats.player_props} props" if stats.player_props > 0 else ""
                    print(f"  ✅ {stats.sport_name}: {stats.events_found} eventos, {stats.total_markets} mercados{props}")
                
                # Delay entre esportes
                if self.delay_between_sports > 0 and i < len(self.sports) - 1:
                    await asyncio.sleep(self.delay_between_sports)
        
        self.tracker.save_all()
        
        total_duration = (datetime.now() - start_time).total_seconds()
        print(f"\n⏱️ Tempo total: {total_duration:.1f}s")
        
        return self.stats
    
    def print_summary(self):
        """Print collection summary."""
        print("\n" + "="*70)
        print("📊 RESUMO DA COLETA")
        print("="*70)
        
        for s in self.stats:
            if s.events_found == 0:
                continue
            props_info = f", {s.player_props} props" if s.player_props > 0 else ""
            
            print(f"  {s.sport_name}: {s.events_found} eventos, {s.total_markets} mercados{props_info}")
        
        print("-"*70)
        total_events = sum(s.events_found for s in self.stats)
        total_markets = sum(s.total_markets for s in self.stats)
        total_props = sum(s.player_props for s in self.stats)
        
        print(f"  TOTAL: {total_events} eventos, {total_markets} mercados, {total_props} player props")
        print("="*70)

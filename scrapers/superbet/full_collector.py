"""
Full Odds Collector for Superbet.
Captures ALL odds from every market, not just player props.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from scrapers.superbet.superbet_client import SuperbetClient
from scrapers.superbet.sport_mapping import SUPERBET_SPORTS, ALL_SPORTS

logger = logging.getLogger(__name__)


@dataclass
class FullCollectionStats:
    """Statistics for full collection."""
    sport_id: int = 0
    sport_name: str = ""
    events_found: int = 0
    total_markets: int = 0
    total_odds: int = 0
    player_props: int = 0
    team_markets: int = 0
    match_markets: int = 0
    parlays: int = 0
    errors: int = 0
    duration_seconds: float = 0


def categorize_market(market_name: str, team1: str = "", team2: str = "") -> str:
    """Categorize a market based on its name."""
    if ';' in market_name:
        return 'parlay'
    if market_name.startswith('Jogador -'):
        return 'player_prop'
    if team1 and team1 in market_name:
        return 'team'
    if team2 and team2 in market_name:
        return 'team'
    return 'match'


def parse_player_prop(market_name: str, outcome_name: str) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Parse player prop details from market and outcome names.
    
    Returns: (player_name, prop_type, line)
    """
    if not market_name.startswith('Jogador -'):
        return None, None, None
    
    # Extract prop type: "Jogador - Marcar Gol" -> "Marcar Gol"
    prop_type = market_name.replace('Jogador - ', '').split(' (')[0]
    
    if ' - Mais de ' in outcome_name:
        parts = outcome_name.split(' - Mais de ')
        player_name = parts[0]
        try:
            line = float(parts[1])
        except (ValueError, IndexError):
            line = None
        return player_name, prop_type, line
    
    elif ' - Menos de ' in outcome_name:
        parts = outcome_name.split(' - Menos de ')
        player_name = parts[0]
        try:
            line = float(parts[1])
        except (ValueError, IndexError):
            line = None
        return player_name, prop_type, line
    
    else:
        return outcome_name, prop_type, None


class FullOddsCollector:
    """Collects ALL odds from Superbet."""
    
    def __init__(self, sports: List[int] = None):
        self.stats: List[FullCollectionStats] = []
        
        # Use provided sports or defaults (main sports with player props)
        if sports:
            self.sport_ids = sports
        else:
            self.sport_ids = [4, 5]  # Basquete, Futebol
    
    async def collect_event_odds(
        self,
        event_id: str,
        event_obj,
        team1: str = "",
        team2: str = "",
    ) -> List[dict]:
        """
        Collect all odds for a single event.
        
        Returns list of parsed odds ready for database insertion.
        """
        odds_list = []
        
        if not event_obj or not event_obj.markets:
            return odds_list
        
        for market in event_obj.markets:
            market_name = market.market_name
            
            for odd in market.odds_list:
                outcome_name = odd.outcome_name
                price = odd.odds
                
                if not market_name or not outcome_name or not price:
                    continue
                
                # Categorize
                category = categorize_market(market_name, team1, team2)
                is_parlay = category == 'parlay'
                is_player_prop = category == 'player_prop'
                
                # Parse player prop details
                player_name = None
                prop_type = None
                line = None
                
                if is_player_prop:
                    player_name, prop_type, line = parse_player_prop(market_name, outcome_name)
                
                odds_list.append({
                    'event_id': event_id,
                    'market_id': market.market_id,
                    'market_name': market_name,
                    'market_category': category,
                    'outcome_name': outcome_name,
                    'price': price,
                    'status': 'active',
                    'is_parlay': is_parlay,
                    'is_player_prop': is_player_prop,
                    'player_name': player_name,
                    'prop_type': prop_type,
                    'line': line,
                    'collected_at': datetime.now(timezone.utc),
                })
        
        return odds_list
    
    async def collect_sport(
        self,
        client: SuperbetClient,
        sport_id: int,
        max_events: int = None,
    ) -> Tuple[FullCollectionStats, List[dict], List[dict]]:
        """
        Collect all events and odds for a sport.
        
        Returns: (stats, events_data, odds_data)
        """
        sport_name = SUPERBET_SPORTS.get(sport_id, f"Sport {sport_id}")
        stats = FullCollectionStats(sport_id=sport_id, sport_name=sport_name)
        events_data = []
        all_odds = []
        
        start_time = datetime.now()
        
        try:
            # Get events list
            events = await client.get_events_by_sport(sport_id)
            stats.events_found = len(events)
            
            print(f"\n🏆 {sport_name}: {len(events)} eventos encontrados")
            
            # Limit events if specified
            events_to_process = events[:max_events] if max_events else events
            
            for event in events_to_process:
                try:
                    event_id = str(event.event_id)
                    
                    # Get full event data with odds
                    full_event = await client.get_event_full_odds(int(event_id))
                    if not full_event:
                        continue
                    
                    # Use correct field names from SuperbetEvent
                    team1 = event.team1 or ""
                    team2 = event.team2 or ""
                    event_name = event.event_name or f"{team1} vs {team2}"
                    
                    # Build event record
                    event_record = {
                        'event_id': event_id,
                        'sport_id': sport_id,
                        'sport_name': sport_name,
                        'tournament_name': event.tournament_name,
                        'team1': team1,
                        'team2': team2,
                        'event_name': event_name,
                        'match_date': event.start_time,
                        'status': event.status,
                    }
                    events_data.append(event_record)
                    
                    # Collect all odds
                    odds = await self.collect_event_odds(event_id, full_event, team1, team2)
                    all_odds.extend(odds)
                    
                    # Update stats
                    stats.total_odds += len(odds)
                    
                    # Count by category
                    for odd in odds:
                        cat = odd['market_category']
                        if cat == 'player_prop':
                            stats.player_props += 1
                        elif cat == 'team':
                            stats.team_markets += 1
                        elif cat == 'parlay':
                            stats.parlays += 1
                        else:
                            stats.match_markets += 1
                    
                    # Unique markets
                    market_names = set(o['market_name'] for o in odds)
                    stats.total_markets += len(market_names)
                    event_record['market_count'] = len(market_names)
                    
                except Exception as e:
                    logger.error(f"Error processing event {event.event_id}: {e}")
                    stats.errors += 1
            
        except Exception as e:
            logger.error(f"Error collecting sport {sport_id}: {e}")
            import traceback
            traceback.print_exc()
            stats.errors += 1
        
        stats.duration_seconds = (datetime.now() - start_time).total_seconds()
        
        print(f"   📊 {stats.total_odds} odds em {stats.total_markets} mercados")
        print(f"   🎯 Props: {stats.player_props} | Team: {stats.team_markets} | Match: {stats.match_markets} | Parlay: {stats.parlays}")
        
        return stats, events_data, all_odds
    
    async def collect_all(self, max_events_per_sport: int = None) -> Tuple[List[FullCollectionStats], List[dict], List[dict]]:
        """
        Collect from all configured sports.
        
        Returns: (all_stats, all_events, all_odds)
        """
        all_stats = []
        all_events = []
        all_odds = []
        
        start_time = datetime.now()
        print("\n" + "="*60)
        print("🚀 FULL ODDS COLLECTION - SUPERBET")
        print("="*60)
        
        async with SuperbetClient() as client:
            for sport_id in self.sport_ids:
                stats, events, odds = await self.collect_sport(client, sport_id, max_events_per_sport)
                all_stats.append(stats)
                all_events.extend(events)
                all_odds.extend(odds)
        
        total_duration = (datetime.now() - start_time).total_seconds()
        
        # Summary
        print("\n" + "="*60)
        print("📊 RESUMO FINAL")
        print("="*60)
        print(f"⏱️  Tempo total: {total_duration:.1f}s")
        print(f"📅 Eventos: {len(all_events)}")
        print(f"🎰 Total de odds: {len(all_odds)}")
        print(f"🎯 Player props: {sum(s.player_props for s in all_stats)}")
        print(f"⚽ Team markets: {sum(s.team_markets for s in all_stats)}")
        print(f"📍 Match markets: {sum(s.match_markets for s in all_stats)}")
        print(f"🔗 Parlays: {sum(s.parlays for s in all_stats)}")
        
        return all_stats, all_events, all_odds


async def test_collection():
    """Test the full collection."""
    # Test with Basquete and Futebol
    collector = FullOddsCollector(sports=[4, 5])
    
    # Limit to 10 events per sport for testing
    stats, events, odds = await collector.collect_all(max_events_per_sport=10)
    
    # Show sample
    print("\n" + "="*60)
    print("📋 SAMPLE - Primeiro evento:")
    print("="*60)
    
    if events:
        event = events[0]
        print(f"Event: {event['event_name']}")
        print(f"Teams: {event['team1']} vs {event['team2']}")
        print(f"Date: {event['match_date']}")
        
        event_odds = [o for o in odds if o['event_id'] == event['event_id']]
        print(f"Odds: {len(event_odds)}")
        
        # Show by category
        for cat in ['match', 'team', 'player_prop', 'parlay']:
            cat_odds = [o for o in event_odds if o['market_category'] == cat]
            if cat_odds:
                print(f"\n{cat.upper()} ({len(cat_odds)}):")
                for o in cat_odds[:3]:
                    mkt = o['market_name'][:50] if len(o['market_name']) > 50 else o['market_name']
                    out = o['outcome_name'][:30] if len(o['outcome_name']) > 30 else o['outcome_name']
                    print(f"  {mkt}: {out} @ {o['price']}")


if __name__ == "__main__":
    asyncio.run(test_collection())


async def collect_and_save():
    """Collect all odds and save to database."""
    from scrapers.superbet.db_storage import SuperbetDBStorage
    
    collector = FullOddsCollector(sports=[4, 5])  # Basquete e Futebol
    
    print("\n" + "="*60)
    print("🚀 FULL COLLECTION + SAVE TO DB")
    print("="*60)
    
    async with SuperbetClient() as client:
        async with SuperbetDBStorage() as storage:
            total_events = 0
            total_odds = 0
            
            for sport_id in collector.sport_ids:
                sport_name = SUPERBET_SPORTS.get(sport_id, f"Sport {sport_id}")
                print(f"\n🏆 Coletando {sport_name}...")
                
                try:
                    events = await client.get_events_by_sport(sport_id)
                    print(f"   {len(events)} eventos encontrados")
                    
                    for event in events[:10]:  # Limit for test
                        try:
                            # Get full odds
                            full_event = await client.get_event_full_odds(int(event.event_id))
                            if not full_event:
                                continue
                            
                            # Save to DB using existing method
                            await storage.save_full_event(full_event, sport_id)
                            total_events += 1
                            
                            if full_event.markets:
                                for m in full_event.markets:
                                    total_odds += len(m.odds_list)
                            
                        except Exception as e:
                            print(f"   ❌ Error saving event {event.event_id}: {e}")
                    
                except Exception as e:
                    print(f"   ❌ Error with sport {sport_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Show stats
            stats = await storage.get_stats()
            print("\n" + "="*60)
            print("📊 RESULTADO:")
            print("="*60)
            print(f"   Eventos salvos: {total_events}")
            print(f"   Odds processadas: {total_odds}")
            print(f"   DB Stats: {stats}")

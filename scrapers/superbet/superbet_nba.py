"""Superbet integration for NBA with player registry mapping."""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import date, timedelta

from .superbet_client import SuperbetClient
from .base import SuperbetEvent, SuperbetMarket, SuperbetOdds
from utils.player_registry import player_registry
from utils.logger import log


logger = logging.getLogger(__name__)


class SuperbetNBA:
    """Superbet NBA data fetcher with player registry integration.
    
    Fetches NBA odds from Superbet and maps players to external IDs
    for cross-referencing with historical stats.
    """
    
    def __init__(self, client: Optional[SuperbetClient] = None):
        """
        Initialize NBA fetcher.
        
        Args:
            client: SuperbetClient instance (creates new if None)
        """
        self.client = client
        self._owned_client = client is None
        self.player_registry = player_registry
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self._owned_client:
            self.client = SuperbetClient()
            await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._owned_client and self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_nba_matches(
        self,
        days_ahead: int = 7,
        include_live: bool = True
    ) -> List[SuperbetEvent]:
        """
        Get NBA matches with odds.
        
        Args:
            days_ahead: Number of days to look ahead
            include_live: Include live matches
            
        Returns:
            List of SuperbetEvent objects
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Note: Basketball might be sport_id 1 in Superbet
        # This needs to be confirmed, using 1 as common basketball ID
        sport_id = 1  # Basketball/NBA
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        try:
            # Fetch scheduled matches
            scheduled = await self.client.get_events_by_sport(
                sport_id=sport_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Fetch live matches if requested
            live = []
            if include_live:
                live = await self.client.get_live_events(sport_id=sport_id)
            
            # Combine and deduplicate
            all_matches = live + scheduled
            seen_ids = set()
            unique_matches = []
            
            for match in all_matches:
                if match.event_id not in seen_ids:
                    seen_ids.add(match.event_id)
                    # Filter for NBA only (not other basketball leagues)
                    if self._is_nba_event(match):
                        unique_matches.append(match)
            
            log.info(f"Fetched {len(unique_matches)} NBA matches from Superbet")
            return unique_matches
            
        except Exception as e:
            log.error(f"Failed to fetch NBA matches: {e}")
            return []
    
    def _is_nba_event(self, event: SuperbetEvent) -> bool:
        """Check if event is an NBA event."""
        nba_keywords = ['NBA', 'National Basketball Association']
        tournament_name = event.tournament_name or ""
        event_name = event.event_name or ""
        
        return any(keyword in tournament_name or keyword in event_name 
                  for keyword in nba_keywords)
    
    async def get_player_props(self, days_ahead: int = 1) -> List[Dict[str, Any]]:
        """
        Get NBA player prop markets.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of player prop dictionaries with player registry mapping
        """
        matches = await self.get_nba_matches(days_ahead=days_ahead)
        
        player_props = []
        
        for match in matches:
            for market in match.markets:
                # Look for player prop markets
                if self._is_player_prop_market(market):
                    prop_data = self._parse_player_prop(market, match)
                    if prop_data:
                        # Try to map player in registry
                        external_id = self._map_player_id(prop_data['player_name'])
                        prop_data['external_player_id'] = external_id
                        player_props.append(prop_data)
        
        log.info(f"Found {len(player_props)} player props")
        return player_props
    
    def _is_player_prop_market(self, market: SuperbetMarket) -> bool:
        """Check if market is a player prop."""
        prop_keywords = [
            'points', 'rebounds', 'assists', 'steals', 'blocks',
            'three pointers', '3-pointers', 'player', 'jogador'
        ]
        market_name_lower = market.market_name.lower()
        
        return any(keyword in market_name_lower for keyword in prop_keywords)
    
    def _parse_player_prop(self, market: SuperbetMarket, match: SuperbetEvent) -> Optional[Dict[str, Any]]:
        """Parse player prop market into structured data."""
        try:
            # Extract player name from market name
            # Format is typically: "Player Name - Points Over/Under 25.5"
            market_name = market.market_name
            
            # Try to extract player name and stat type
            parts = market_name.split('-')
            if len(parts) < 2:
                return None
            
            player_name = parts[0].strip()
            stat_description = parts[1].strip() if len(parts) > 1 else market_name
            
            # Extract line value from outcomes
            line_value = None
            over_odds = None
            under_odds = None
            
            for odds in market.odds_list:
                outcome_lower = odds.outcome_name.lower()
                if 'over' in outcome_lower or 'acima' in outcome_lower:
                    over_odds = odds.odds
                    # Try to extract line from outcome name
                    try:
                        numbers = [float(s) for s in odds.outcome_name.split() if s.replace('.', '').isdigit()]
                        if numbers:
                            line_value = numbers[0]
                    except:
                        pass
                elif 'under' in outcome_lower or 'abaixo' in outcome_lower:
                    under_odds = odds.odds
                    # Extract line from outcome name
                    try:
                        numbers = [float(s) for s in odds.outcome_name.split() if s.replace('.', '').replace('-', '').isdigit()]
                        if numbers and not line_value:
                            line_value = numbers[0]
                    except (ValueError, AttributeError):
                        pass
            
            return {
                'event_id': match.event_id,
                'event_name': match.event_name,
                'start_time': match.start_time,
                'player_name': player_name,
                'stat_type': stat_description,
                'line': line_value,
                'over_odds': over_odds,
                'under_odds': under_odds,
                'market_id': market.market_id,
                'team1': match.team1,
                'team2': match.team2,
            }
            
        except Exception as e:
            log.warning(f"Failed to parse player prop: {e}")
            return None
    
    def _map_player_id(self, player_name: str) -> Optional[str]:
        """Map player name to external ID using player registry."""
        try:
            # Try exact match first
            player = self.player_registry.get_player(player_name)
            if player and player.get('sport') == 'nba':
                return player.get('external_id')
            
            # Try fuzzy match
            player = self.player_registry.find_player_fuzzy(player_name, sport='nba', threshold=0.8)
            if player:
                log.debug(f"Mapped '{player_name}' to external ID: {player.get('external_id')}")
                return player.get('external_id')
            
            log.debug(f"No player mapping found for player: {player_name}")
            return None
            
        except Exception as e:
            log.warning(f"Error mapping player {player_name}: {e}")
            return None
    
    async def get_moneyline_odds(self, days_ahead: int = 1) -> List[Dict[str, Any]]:
        """
        Get NBA moneyline odds.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of moneyline odds dictionaries
        """
        matches = await self.get_nba_matches(days_ahead=days_ahead)
        
        moneyline_odds = []
        
        for match in matches:
            for market in match.markets:
                if self._is_moneyline_market(market):
                    odds_data = {
                        'event_id': match.event_id,
                        'event_name': match.event_name,
                        'start_time': match.start_time,
                        'team1': match.team1,
                        'team2': match.team2,
                        'market_type': 'moneyline',
                    }
                    
                    for odds in market.odds_list:
                        if match.team1.lower() in odds.outcome_name.lower():
                            odds_data['team1_odds'] = odds.odds
                        elif match.team2.lower() in odds.outcome_name.lower():
                            odds_data['team2_odds'] = odds.odds
                    
                    if 'team1_odds' in odds_data and 'team2_odds' in odds_data:
                        moneyline_odds.append(odds_data)
                        break
        
        return moneyline_odds
    
    def _is_moneyline_market(self, market: SuperbetMarket) -> bool:
        """Check if market is moneyline/match winner."""
        moneyline_keywords = ['winner', 'vencedor', 'resultado final', 'match result']
        market_name_lower = market.market_name.lower()
        
        return any(keyword in market_name_lower for keyword in moneyline_keywords)
    
    async def get_over_under_odds(self, days_ahead: int = 1) -> List[Dict[str, Any]]:
        """
        Get NBA over/under (totals) odds.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of over/under odds dictionaries
        """
        matches = await self.get_nba_matches(days_ahead=days_ahead)
        
        totals_odds = []
        
        for match in matches:
            for market in match.markets:
                if self._is_totals_market(market):
                    odds_data = {
                        'event_id': match.event_id,
                        'event_name': match.event_name,
                        'start_time': match.start_time,
                        'team1': match.team1,
                        'team2': match.team2,
                        'market_type': 'over_under',
                    }
                    
                    for odds in market.odds_list:
                        outcome_lower = odds.outcome_name.lower()
                        if 'over' in outcome_lower or 'acima' in outcome_lower:
                            odds_data['over_odds'] = odds.odds
                            # Extract line
                            try:
                                numbers = [float(s) for s in odds.outcome_name.split() if s.replace('.', '').isdigit()]
                                if numbers:
                                    odds_data['line'] = numbers[0]
                            except:
                                pass
                        elif 'under' in outcome_lower or 'abaixo' in outcome_lower:
                            odds_data['under_odds'] = odds.odds
                    
                    if 'over_odds' in odds_data and 'under_odds' in odds_data:
                        totals_odds.append(odds_data)
                        break
        
        return totals_odds
    
    def _is_totals_market(self, market: SuperbetMarket) -> bool:
        """Check if market is totals/over-under."""
        totals_keywords = ['total points', 'total de pontos', 'over/under', 'acima/abaixo']
        market_name_lower = market.market_name.lower()
        
        return any(keyword in market_name_lower for keyword in totals_keywords)

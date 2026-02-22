"""Populate esports tournaments data - matches, map stats, player stats, team stats.

This script collects COMPLETE tournament data for multiple esports.
"""
import asyncio
import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db_session, init_db
from database.historical_models import (
    EsportsMatch, EsportsMapStats, EsportsPlayerStats, EsportsTeamStats
)
from utils.logger import log

# Try to import scrapers - they may not all be available
try:
    from scrapers.vlr.vlr_unified import VLRUnified
except ImportError:
    VLRUnified = None
    
try:
    from scrapers.hltv.hltv_unified import HLTVUnified
except ImportError:
    HLTVUnified = None
    
try:
    from scrapers.lol.lol_unified import LoLUnified
except ImportError:
    LoLUnified = None
    
try:
    from scrapers.dota.dota_unified import DotaUnified
except ImportError:
    DotaUnified = None


class EsportsTournamentPopulator:
    """Populates esports tournament data into historical database."""
    
    def __init__(self):
        """Initialize populator."""
        self.db = get_db_session()
        
    async def populate_all_esports(self, days_back: int = 120):
        """Populate all esports.
        
        Args:
            days_back: Number of days to go back (default 120 for ~4 months)
        """
        log.info("Starting esports tournaments population...")
        
        try:
            # Valorant
            await self.populate_valorant(days_back)
            
            # CS2
            await self.populate_cs2(days_back)
            
            # League of Legends
            await self.populate_lol(days_back)
            
            # Dota 2
            await self.populate_dota(days_back)
            
            log.info("\nAll esports population complete!")
            
        finally:
            self.db.close()
    
    async def populate_valorant(self, days_back: int):
        """Populate Valorant matches.
        
        Args:
            days_back: Number of days to go back
        """
        log.info("\n" + "="*60)
        log.info("Processing Valorant")
        log.info("="*60)
        
        if not VLRUnified:
            log.warning("VLRUnified scraper not available, skipping Valorant")
            return
        
        try:
            vlr = VLRUnified()
            matches_added = 0
            
            # Get recent matches using correct method
            matches = await vlr.get_results(num_pages=1)
            
            for match_data in matches:
                match = self._parse_valorant_match(match_data)
                if match:
                    self.db.merge(EsportsMatch(**match))
                    matches_added += 1
            
            self.db.commit()
            log.info(f"Valorant: {matches_added} matches added")
            
            # Calculate team stats
            await self._calculate_esports_team_stats('valorant')
            
        except Exception as e:
            log.error(f"Error populating Valorant: {e}")
            self.db.rollback()
    
    async def populate_cs2(self, days_back: int):
        """Populate CS2 matches.
        
        Args:
            days_back: Number of days to go back
        """
        log.info("\n" + "="*60)
        log.info("Processing CS2")
        log.info("="*60)
        
        if not HLTVUnified:
            log.warning("HLTVUnified scraper not available, skipping CS2")
            return
        
        try:
            hltv = HLTVUnified()
            matches_added = 0
            
            # Get recent matches using correct method (already async)
            matches = await hltv.get_results(limit=100)
            
            for match_data in matches:
                match = self._parse_cs2_match(match_data)
                if match:
                    self.db.merge(EsportsMatch(**match))
                    matches_added += 1
            
            self.db.commit()
            log.info(f"CS2: {matches_added} matches added")
            
            # Calculate team stats
            await self._calculate_esports_team_stats('cs2')
            
        except Exception as e:
            log.error(f"Error populating CS2: {e}")
            self.db.rollback()
    
    async def populate_lol(self, days_back: int):
        """Populate League of Legends matches.
        
        Args:
            days_back: Number of days to go back
        """
        log.info("\n" + "="*60)
        log.info("Processing League of Legends")
        log.info("="*60)
        
        if not LoLUnified:
            log.warning("LoLUnified scraper not available, skipping LoL")
            return
        
        try:
            lol = LoLUnified()
            matches_added = 0
            
            # Get completed matches using correct method
            matches = await lol.get_completed_matches()
            
            for match_data in matches:
                match = self._parse_lol_match(match_data)
                if match:
                    self.db.merge(EsportsMatch(**match))
                    matches_added += 1
            
            self.db.commit()
            log.info(f"LoL: {matches_added} matches added")
            
            # Calculate team stats
            await self._calculate_esports_team_stats('lol')
            
        except Exception as e:
            log.error(f"Error populating LoL: {e}")
            self.db.rollback()
    
    async def populate_dota(self, days_back: int):
        """Populate Dota 2 matches.
        
        Args:
            days_back: Number of days to go back
        """
        log.info("\n" + "="*60)
        log.info("Processing Dota 2")
        log.info("="*60)
        
        if not DotaUnified:
            log.warning("DotaUnified scraper not available, skipping Dota 2")
            return
        
        try:
            dota = DotaUnified()
            matches_added = 0
            
            # Get pro matches using correct method
            matches = await dota.get_pro_matches(limit=100)
            
            for match_data in matches:
                match = self._parse_dota_match(match_data)
                if match:
                    self.db.merge(EsportsMatch(**match))
                    matches_added += 1
            
            self.db.commit()
            log.info(f"Dota 2: {matches_added} matches added")
            
            # Calculate team stats
            await self._calculate_esports_team_stats('dota2')
            
        except Exception as e:
            log.error(f"Error populating Dota 2: {e}")
            self.db.rollback()
    
    def _parse_valorant_match(self, match_data) -> Optional[Dict]:
        """Parse Valorant match data.
        
        Args:
            match_data: ValorantResult object (not dict!)
            
        Returns:
            Parsed match dict or None
        """
        try:
            # Generate unique match_id from match_page or use UUID
            if match_data.match_page:
                match_id = match_data.match_page
            else:
                # Use UUID with null-byte separated fields to avoid collisions
                unique_str = f"{match_data.team1}\x00{match_data.team2}\x00{match_data.time_completed}\x00{match_data.match_event}"
                match_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_str))
            
            # ValorantResult is a dataclass - access attributes directly
            # Safely handle score comparison
            try:
                score1 = int(match_data.score1) if match_data.score1 else 0
                score2 = int(match_data.score2) if match_data.score2 else 0
            except (ValueError, TypeError):
                score1 = 0
                score2 = 0
            
            # Determine winner (handle ties)
            if score1 > score2:
                winner = match_data.team1
            elif score2 > score1:
                winner = match_data.team2
            else:
                winner = ''  # Tie or unknown
            
            return {
                'match_id': match_id,
                'game': 'valorant',
                'tournament': match_data.match_event if match_data.match_event else 'Unknown',
                'tournament_tier': 'C',  # Default tier
                'match_date': datetime.now(),  # time_completed is string, use now for simplicity
                'team1': match_data.team1,
                'team2': match_data.team2,
                'team1_score': score1,
                'team2_score': score2,
                'winner': winner,
                'best_of': 3,  # Default
            }
        except Exception as e:
            log.error(f"Error parsing Valorant match: {e}")
            return None
    
    def _parse_cs2_match(self, match_data) -> Optional[Dict]:
        """Parse CS2 match data.
        
        Args:
            match_data: MatchResult object (not dict!)
            
        Returns:
            Parsed match dict or None
        """
        try:
            # MatchResult is a dataclass - access attributes directly
            # Safely handle team names
            team1_name = match_data.team1.name if match_data.team1 else 'Unknown'
            team2_name = match_data.team2.name if match_data.team2 else 'Unknown'
            
            # Determine winner (handle ties)
            if match_data.team1_score > match_data.team2_score:
                winner = team1_name
            elif match_data.team2_score > match_data.team1_score:
                winner = team2_name
            else:
                winner = ''  # Tie or unknown
            
            return {
                'match_id': str(match_data.id),
                'game': 'cs2',
                'tournament': match_data.event if match_data.event else 'Unknown',
                'tournament_tier': 'C',  # Default tier
                'match_date': match_data.date if match_data.date else datetime.now(),
                'team1': team1_name,
                'team2': team2_name,
                'team1_score': match_data.team1_score,
                'team2_score': match_data.team2_score,
                'winner': winner,
                'best_of': 3,  # Default
            }
        except Exception as e:
            log.error(f"Error parsing CS2 match: {e}")
            return None
    
    def _parse_lol_match(self, match_data) -> Optional[Dict]:
        """Parse LoL match data.
        
        Args:
            match_data: LoLMatch object (not dict!)
            
        Returns:
            Parsed match dict or None
        """
        try:
            # LoLMatch is a dataclass - access attributes directly
            # Determine winner (handle ties)
            if match_data.team1_wins > match_data.team2_wins:
                winner = match_data.team1_name
            elif match_data.team2_wins > match_data.team1_wins:
                winner = match_data.team2_name
            else:
                winner = ''  # Tie or unknown
            
            return {
                'match_id': match_data.id,
                'game': 'lol',
                'tournament': match_data.league_name,
                'tournament_tier': 'A' if match_data.league_slug in ['lck', 'lpl', 'lec', 'lcs'] else 'B',
                'match_date': match_data.start_time,
                'team1': match_data.team1_name,
                'team2': match_data.team2_name,
                'team1_score': match_data.team1_wins,
                'team2_score': match_data.team2_wins,
                'winner': winner,
                'best_of': match_data.best_of,
            }
        except Exception as e:
            log.error(f"Error parsing LoL match: {e}")
            return None
    
    def _parse_dota_match(self, match_data) -> Optional[Dict]:
        """Parse Dota 2 match data.
        
        Args:
            match_data: DotaProMatch object (not dict!)
            
        Returns:
            Parsed match dict or None
        """
        try:
            # DotaProMatch is a dataclass - access attributes directly
            winner = ''
            if match_data.radiant_win is not None:
                winner = match_data.radiant_name if match_data.radiant_win else match_data.dire_name
            
            return {
                'match_id': str(match_data.match_id),
                'game': 'dota2',
                'tournament': match_data.league_name if match_data.league_name else 'Unknown',
                'tournament_tier': 'C',  # Default tier
                'match_date': datetime.fromtimestamp(match_data.start_time) if match_data.start_time else datetime.now(),
                'team1': match_data.radiant_name if match_data.radiant_name else 'Radiant',
                'team2': match_data.dire_name if match_data.dire_name else 'Dire',
                'team1_score': match_data.radiant_score,
                'team2_score': match_data.dire_score,
                'winner': winner,
                'best_of': 1,  # Dota matches are typically Bo1 or series
            }
        except Exception as e:
            log.error(f"Error parsing Dota 2 match: {e}")
            return None
    
    async def _calculate_esports_team_stats(self, game: str):
        """Calculate aggregated team statistics from matches.
        
        Args:
            game: Game name ('valorant', 'cs2', 'lol', 'dota2')
        """
        log.info(f"Calculating team stats for {game}...")
        
        # Query all matches for this game
        matches = self.db.query(EsportsMatch).filter(EsportsMatch.game == game).all()
        
        teams = {}
        
        for match in matches:
            # Process team1
            if match.team1 not in teams:
                teams[match.team1] = {
                    'matches_played': 0, 'matches_won': 0, 'matches_lost': 0,
                    'maps_won': 0, 'maps_lost': 0,
                }
            
            # Process team2
            if match.team2 not in teams:
                teams[match.team2] = {
                    'matches_played': 0, 'matches_won': 0, 'matches_lost': 0,
                    'maps_won': 0, 'maps_lost': 0,
                }
            
            # Update stats
            teams[match.team1]['matches_played'] += 1
            teams[match.team2]['matches_played'] += 1
            
            if match.winner == match.team1:
                teams[match.team1]['matches_won'] += 1
                teams[match.team2]['matches_lost'] += 1
            elif match.winner == match.team2:
                teams[match.team2]['matches_won'] += 1
                teams[match.team1]['matches_lost'] += 1
            
            # Maps
            if match.team1_score:
                teams[match.team1]['maps_won'] += match.team1_score
            if match.team2_score:
                teams[match.team1]['maps_lost'] += match.team2_score
                teams[match.team2]['maps_won'] += match.team2_score
            if match.team1_score:
                teams[match.team2]['maps_lost'] += match.team1_score
        
        # Save team stats
        for team_name, stats in teams.items():
            played = stats['matches_played']
            maps_played = stats['maps_won'] + stats['maps_lost']
            
            if played == 0:
                continue
            
            team_stats = EsportsTeamStats(
                team=team_name,
                game=game,
                period=datetime.now().strftime("%Y-%m"),
                matches_played=played,
                matches_won=stats['matches_won'],
                matches_lost=stats['matches_lost'],
                win_rate=(stats['matches_won'] / played * 100) if played > 0 else 0,
                maps_played=maps_played,
                maps_won=stats['maps_won'],
                maps_lost=stats['maps_lost'],
                map_win_rate=(stats['maps_won'] / maps_played * 100) if maps_played > 0 else 0,
            )
            self.db.merge(team_stats)
        
        self.db.commit()
        log.info(f"Team stats calculated for {len(teams)} teams")


async def main():
    """Main execution."""
    # Initialize database
    init_db()
    
    # Populate all esports
    populator = EsportsTournamentPopulator()
    await populator.populate_all_esports(days_back=120)
    
    log.info("Esports tournaments population complete!")


if __name__ == "__main__":
    asyncio.run(main())

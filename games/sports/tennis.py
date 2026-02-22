"""Tennis game implementation."""

from typing import Dict, Any, List, Optional
from games.base import Game


class Tennis(Game):
    """Tennis game handler."""
    
    def __init__(self):
        """Initialize Tennis game."""
        super().__init__(
            name="Tennis",
            identifier="tennis",
            category="sports"
        )
    
    def get_markets(self) -> List[str]:
        """
        Get available betting markets for tennis.
        
        Returns:
            List of market names
        """
        return [
            "match_winner",        # Winner of the match
            "set_winner",          # Winner of a specific set
            "total_games",         # Over/Under total games
            "handicap_games",      # Games handicap
            "exact_score",         # Exact set score
            "first_set_winner",    # Winner of first set
        ]
    
    def get_supported_tournaments(self) -> List[str]:
        """
        Get supported tennis tournaments.
        
        Returns:
            List of tournament names
        """
        return [
            "Australian Open",
            "French Open (Roland Garros)",
            "Wimbledon",
            "US Open",
            "ATP Tour",
            "WTA Tour",
            "Davis Cup",
            "Billie Jean King Cup",
            "ATP Masters 1000",
            "WTA 1000",
        ]
    
    def validate_match_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate tennis match data.
        
        Args:
            data: Match data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['player1', 'player2', 'tournament']
        return all(field in data for field in required_fields)
    
    def calculate_implied_probability(
        self,
        player1_odds: float,
        player2_odds: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate implied probabilities from odds.
        
        Args:
            player1_odds: Odds for player 1
            player2_odds: Odds for player 2 (optional)
            
        Returns:
            Dictionary with probabilities
        """
        player1_prob = 1 / player1_odds if player1_odds > 0 else 0
        
        result = {'player1': player1_prob}
        
        if player2_odds:
            player2_prob = 1 / player2_odds if player2_odds > 0 else 0
            result['player2'] = player2_prob
            
            # Calculate overround (bookmaker margin)
            total = player1_prob + player2_prob
            result['overround'] = total - 1.0 if total > 1.0 else 0.0
        
        return result
    
    def get_player_surfaces(self) -> List[str]:
        """
        Get tennis court surfaces.
        
        Returns:
            List of surface types
        """
        return [
            "Hard Court",
            "Clay Court",
            "Grass Court",
            "Carpet",
        ]
    
    def get_match_formats(self) -> Dict[str, str]:
        """
        Get tennis match formats.
        
        Returns:
            Dictionary of format names and descriptions
        """
        return {
            "best_of_3": "Best of 3 sets (ATP 250-500, WTA)",
            "best_of_5": "Best of 5 sets (Grand Slams, ATP Masters Finals)",
        }

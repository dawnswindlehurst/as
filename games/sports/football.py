"""Football (soccer) game implementation."""

from typing import Dict, Any, List, Optional
from games.base import Game


class Football(Game):
    """Football (soccer) game handler."""
    
    def __init__(self):
        """Initialize Football game."""
        super().__init__(
            name="Football",
            identifier="football",
            category="sports"
        )
    
    def get_markets(self) -> List[str]:
        """
        Get available betting markets for football.
        
        Returns:
            List of market names
        """
        return [
            "1x2",                    # Match result (Home/Draw/Away)
            "double_chance",          # Double chance
            "both_teams_to_score",    # Both teams to score
            "over_under_goals",       # Over/Under total goals
            "correct_score",          # Exact score
            "half_time_full_time",    # HT/FT result
            "asian_handicap",         # Asian handicap
            "first_goal_scorer",      # First goal scorer
            "anytime_goal_scorer",    # Anytime goal scorer
            "total_corners",          # Total corners
            "total_cards",            # Total cards
        ]
    
    def get_supported_leagues(self) -> List[str]:
        """
        Get supported football leagues.
        
        Returns:
            List of league names
        """
        return [
            "Brasileirão Série A",
            "Brasileirão Série B",
            "Copa do Brasil",
            "Copa Libertadores",
            "Copa Sul-Americana",
            "UEFA Champions League",
            "UEFA Europa League",
            "Premier League (England)",
            "La Liga (Spain)",
            "Serie A (Italy)",
            "Bundesliga (Germany)",
            "Ligue 1 (France)",
            "World Cup",
            "Copa América",
            "UEFA European Championship",
        ]
    
    def validate_match_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate football match data.
        
        Args:
            data: Match data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['home_team', 'away_team', 'league']
        return all(field in data for field in required_fields)
    
    def calculate_implied_probability(
        self,
        home_odds: float,
        draw_odds: Optional[float] = None,
        away_odds: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate implied probabilities from 1X2 odds.
        
        Args:
            home_odds: Odds for home win
            draw_odds: Odds for draw (optional)
            away_odds: Odds for away win (optional)
            
        Returns:
            Dictionary with probabilities
        """
        home_prob = 1 / home_odds if home_odds > 0 else 0
        
        result = {'home': home_prob}
        
        if draw_odds:
            draw_prob = 1 / draw_odds if draw_odds > 0 else 0
            result['draw'] = draw_prob
        
        if away_odds:
            away_prob = 1 / away_odds if away_odds > 0 else 0
            result['away'] = away_prob
        
        # Calculate overround (bookmaker margin)
        if draw_odds and away_odds:
            total = home_prob + draw_prob + away_prob
            result['overround'] = total - 1.0 if total > 1.0 else 0.0
        
        return result
    
    def get_match_statistics_fields(self) -> List[str]:
        """
        Get common match statistics fields.
        
        Returns:
            List of statistics field names
        """
        return [
            "possession",
            "shots",
            "shots_on_target",
            "corners",
            "fouls",
            "yellow_cards",
            "red_cards",
            "offsides",
            "passes",
            "pass_accuracy",
            "expected_goals",  # xG
        ]
    
    def get_competition_tiers(self) -> Dict[str, List[str]]:
        """
        Get competitions organized by tier.
        
        Returns:
            Dictionary of tiers to competition lists
        """
        return {
            "tier_1": [
                "UEFA Champions League",
                "Premier League",
                "La Liga",
                "Serie A",
                "Bundesliga",
                "World Cup",
            ],
            "tier_2": [
                "UEFA Europa League",
                "Ligue 1",
                "Brasileirão Série A",
                "Copa Libertadores",
                "Copa América",
            ],
            "tier_3": [
                "Copa do Brasil",
                "Copa Sul-Americana",
                "Brasileirão Série B",
                "Championship (England)",
            ],
        }

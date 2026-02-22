"""Edge finder - identify betting opportunities."""
from typing import List, Dict, Optional
from config.settings import MIN_CONFIDENCE, MIN_EDGE, MAX_EDGE
from utils.helpers import calculate_implied_probability, calculate_edge
from utils.logger import log


class EdgeFinder:
    """Find betting edges by comparing model probabilities with market odds."""
    
    def __init__(
        self,
        min_confidence: float = MIN_CONFIDENCE,
        min_edge: float = MIN_EDGE,
        max_edge: float = MAX_EDGE,
    ):
        self.min_confidence = min_confidence
        self.min_edge = min_edge
        self.max_edge = max_edge
    
    def find_edges(
        self, model_prob: float, market_odds: float
    ) -> Optional[Dict]:
        """Find edge for a single bet.
        
        Args:
            model_prob: Model's probability estimate (0-1)
            market_odds: Market decimal odds
            
        Returns:
            Edge dictionary or None if no edge
        """
        if model_prob < self.min_confidence:
            log.debug(f"Rejected: confidence {model_prob:.2%} below minimum {self.min_confidence:.2%}")
            return None
        
        market_prob = calculate_implied_probability(market_odds)
        edge = calculate_edge(model_prob, market_prob)
        
        # Check if edge meets criteria
        if edge < self.min_edge or edge > self.max_edge:
            return None
        
        return {
            "model_probability": model_prob,
            "market_probability": market_prob,
            "market_odds": market_odds,
            "edge": edge,
            "edge_percent": edge * 100,
        }
    
    def find_best_edge(
        self, model_prob: float, bookmaker_odds: Dict[str, float]
    ) -> Optional[Dict]:
        """Find best edge across multiple bookmakers.
        
        Args:
            model_prob: Model's probability estimate
            bookmaker_odds: Dictionary of {bookmaker: odds}
            
        Returns:
            Best edge dictionary or None
        """
        best_edge = None
        best_edge_value = 0.0
        
        for bookmaker, odds in bookmaker_odds.items():
            edge_info = self.find_edges(model_prob, odds)
            
            if edge_info and edge_info["edge"] > best_edge_value:
                best_edge_value = edge_info["edge"]
                best_edge = {**edge_info, "bookmaker": bookmaker}
        
        return best_edge
    
    def scan_opportunities(
        self, predictions: List[Dict], odds_data: List[Dict]
    ) -> List[Dict]:
        """Scan for betting opportunities across multiple matches.
        
        Args:
            predictions: List of model predictions
            odds_data: List of odds data
            
        Returns:
            List of opportunities
        """
        opportunities = []
        
        for pred in predictions:
            match_id = pred.get("match_id")
            
            # Find corresponding odds
            match_odds = [o for o in odds_data if o.get("match_id") == match_id]
            
            if not match_odds:
                continue
            
            # Check team1 edge
            team1_odds = {o["bookmaker"]: o["team1_odds"] for o in match_odds if o.get("team1_odds")}
            if team1_odds:
                team1_edge = self.find_best_edge(pred["team1_win_prob"], team1_odds)
                if team1_edge:
                    opportunities.append({
                        "match_id": match_id,
                        "selection": "team1",
                        **team1_edge,
                    })
            
            # Check team2 edge
            team2_odds = {o["bookmaker"]: o["team2_odds"] for o in match_odds if o.get("team2_odds")}
            if team2_odds:
                team2_edge = self.find_best_edge(pred["team2_win_prob"], team2_odds)
                if team2_edge:
                    opportunities.append({
                        "match_id": match_id,
                        "selection": "team2",
                        **team2_edge,
                    })
        
        log.info(f"Found {len(opportunities)} betting opportunities")
        return opportunities

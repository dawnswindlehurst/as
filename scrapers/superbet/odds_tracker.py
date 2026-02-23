"""
Odds and Line Tracker for Superbet.
Tracks:
1. In-game changes: odds/line movements before a game starts
2. Cross-game changes: how player lines evolve across different games
"""
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class OddsSnapshot:
    """Single snapshot of odds at a point in time."""
    timestamp: str
    odds_over: float
    odds_under: float


@dataclass
class LineSnapshot:
    """Single snapshot of line at a point in time."""
    timestamp: str
    line: float
    odds_over: float
    odds_under: float


@dataclass 
class InGameHistory:
    """
    Tracks odds/line changes within a single game.
    Example: Wembanyama Over 23.5 pontos starts at 1.95, moves to 2.10, then 1.85
    """
    event_id: str
    event_name: str  # "Detroit Pistons vs San Antonio Spurs"
    event_date: str
    player_name: str
    prop_type: str  # "Total de Pontos", "Rebotes", etc.
    
    # Opening values (first time seen)
    opening_line: float
    opening_odds_over: float
    opening_odds_under: float
    opening_timestamp: str
    
    # Current values
    current_line: float
    current_odds_over: float
    current_odds_under: float
    last_updated: str
    
    # History of changes
    odds_history: List[OddsSnapshot] = field(default_factory=list)
    line_history: List[LineSnapshot] = field(default_factory=list)
    
    @property
    def odds_swing(self) -> float:
        """Total odds movement from opening (over line)."""
        return round(self.current_odds_over - self.opening_odds_over, 3)
    
    @property
    def line_move(self) -> float:
        """Total line movement from opening."""
        return round(self.current_line - self.opening_line, 1)
    
    @property
    def num_odds_changes(self) -> int:
        return len(self.odds_history)
    
    @property
    def num_line_changes(self) -> int:
        return len(self.line_history)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'event_date': self.event_date,
            'player_name': self.player_name,
            'prop_type': self.prop_type,
            'opening_line': self.opening_line,
            'opening_odds_over': self.opening_odds_over,
            'opening_odds_under': self.opening_odds_under,
            'opening_timestamp': self.opening_timestamp,
            'current_line': self.current_line,
            'current_odds_over': self.current_odds_over,
            'current_odds_under': self.current_odds_under,
            'last_updated': self.last_updated,
            'odds_swing': self.odds_swing,
            'line_move': self.line_move,
            'num_odds_changes': self.num_odds_changes,
            'num_line_changes': self.num_line_changes,
            'odds_history': [asdict(h) for h in self.odds_history],
            'line_history': [asdict(h) for h in self.line_history],
        }


@dataclass
class PlayerGameLine:
    """A player's line for a specific game."""
    event_id: str
    event_name: str
    event_date: str
    line: float
    odds_over: float
    odds_under: float
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class CrossGameHistory:
    """
    Tracks how a player's lines change across different games.
    Example: Wembanyama pontos line was 23.5 vs Pistons, 25.5 vs Lakers, 22.5 vs Celtics
    """
    player_name: str
    prop_type: str
    games: List[PlayerGameLine] = field(default_factory=list)
    
    @property
    def average_line(self) -> float:
        if not self.games:
            return 0.0
        return round(sum(g.line for g in self.games) / len(self.games), 1)
    
    @property
    def highest_line(self) -> Optional[PlayerGameLine]:
        if not self.games:
            return None
        return max(self.games, key=lambda g: g.line)
    
    @property
    def lowest_line(self) -> Optional[PlayerGameLine]:
        if not self.games:
            return None
        return min(self.games, key=lambda g: g.line)
    
    @property
    def line_trend(self) -> str:
        """Returns 'up', 'down', or 'stable' based on last 3 games."""
        if len(self.games) < 2:
            return 'stable'
        recent = sorted(self.games, key=lambda g: g.event_date)[-3:]
        if len(recent) < 2:
            return 'stable'
        diff = recent[-1].line - recent[0].line
        if diff > 0.5:
            return 'up'
        elif diff < -0.5:
            return 'down'
        return 'stable'
    
    def to_dict(self):
        return {
            'player_name': self.player_name,
            'prop_type': self.prop_type,
            'num_games': len(self.games),
            'average_line': self.average_line,
            'highest_line': self.highest_line.to_dict() if self.highest_line else None,
            'lowest_line': self.lowest_line.to_dict() if self.lowest_line else None,
            'line_trend': self.line_trend,
            'games': [g.to_dict() for g in sorted(self.games, key=lambda x: x.event_date, reverse=True)],
        }


class OddsTracker:
    """
    Complete odds and line tracking system.
    
    Features:
    - Track in-game odds/line movements
    - Track cross-game line changes for players
    - Persist all data to JSON files
    - Query historical data
    """
    
    def __init__(self, storage_dir: str = "data/odds_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-game tracking: key = "event_id:player:prop_type"
        self.in_game: Dict[str, InGameHistory] = {}
        
        # Cross-game tracking: key = "player:prop_type"
        self.cross_game: Dict[str, CrossGameHistory] = {}
        
        # Load existing cross-game data
        self._load_cross_game_data()
    
    def _make_in_game_key(self, event_id: str, player_name: str, prop_type: str) -> str:
        return f"{event_id}:{player_name}:{prop_type}"
    
    def _make_cross_game_key(self, player_name: str, prop_type: str) -> str:
        return f"{player_name}:{prop_type}"
    
    def _get_event_file(self, event_id: str) -> Path:
        return self.storage_dir / f"event_{event_id}.json"
    
    def _get_cross_game_file(self) -> Path:
        return self.storage_dir / "cross_game_history.json"
    
    def _load_cross_game_data(self) -> None:
        """Load cross-game historical data."""
        file_path = self._get_cross_game_file()
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for key, hist_data in data.items():
                        games = [
                            PlayerGameLine(**g) for g in hist_data.get('games', [])
                        ]
                        self.cross_game[key] = CrossGameHistory(
                            player_name=hist_data['player_name'],
                            prop_type=hist_data['prop_type'],
                            games=games,
                        )
                logger.info(f"Loaded cross-game history for {len(self.cross_game)} player props")
            except Exception as e:
                logger.error(f"Error loading cross-game data: {e}")
    
    def _save_cross_game_data(self) -> None:
        """Save cross-game historical data."""
        file_path = self._get_cross_game_file()
        data = {k: v.to_dict() for k, v in self.cross_game.items()}
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_event(self, event_id: str) -> None:
        """Load in-game history for a specific event."""
        file_path = self._get_event_file(event_id)
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for key, hist_data in data.get('props', {}).items():
                        self.in_game[key] = InGameHistory(
                            event_id=hist_data['event_id'],
                            event_name=hist_data['event_name'],
                            event_date=hist_data['event_date'],
                            player_name=hist_data['player_name'],
                            prop_type=hist_data['prop_type'],
                            opening_line=hist_data['opening_line'],
                            opening_odds_over=hist_data['opening_odds_over'],
                            opening_odds_under=hist_data['opening_odds_under'],
                            opening_timestamp=hist_data['opening_timestamp'],
                            current_line=hist_data['current_line'],
                            current_odds_over=hist_data['current_odds_over'],
                            current_odds_under=hist_data['current_odds_under'],
                            last_updated=hist_data['last_updated'],
                            odds_history=[OddsSnapshot(**h) for h in hist_data.get('odds_history', [])],
                            line_history=[LineSnapshot(**h) for h in hist_data.get('line_history', [])],
                        )
                logger.info(f"Loaded {len([k for k in self.in_game if k.startswith(event_id)])} props for event {event_id}")
            except Exception as e:
                logger.error(f"Error loading event {event_id}: {e}")
    
    def save_event(self, event_id: str) -> None:
        """Save in-game history for a specific event."""
        file_path = self._get_event_file(event_id)
        event_props = {
            k: v.to_dict() for k, v in self.in_game.items() 
            if k.startswith(f"{event_id}:")
        }
        
        data = {
            'event_id': event_id,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'props': event_props,
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(event_props)} props for event {event_id}")
    
    def update_prop(
        self,
        event_id: str,
        event_name: str,
        event_date: str,
        player_name: str,
        prop_type: str,
        line: float,
        odds_over: float,
        odds_under: float,
    ) -> Dict[str, any]:
        """
        Update a prop with new values. Tracks both in-game and cross-game changes.
        
        Returns:
            Dict with 'odds_changed', 'line_changed', 'is_new' flags and details
        """
        now = datetime.now(timezone.utc).isoformat()
        in_game_key = self._make_in_game_key(event_id, player_name, prop_type)
        cross_game_key = self._make_cross_game_key(player_name, prop_type)
        
        result = {
            'is_new': False,
            'odds_changed': False,
            'line_changed': False,
            'odds_swing': 0.0,
            'line_move': 0.0,
            'old_odds': None,
            'new_odds': odds_over,
            'old_line': None,
            'new_line': line,
        }
        
        # === IN-GAME TRACKING ===
        if in_game_key in self.in_game:
            hist = self.in_game[in_game_key]
            
            # Check for line change
            if abs(hist.current_line - line) > 0.01:
                result['line_changed'] = True
                result['old_line'] = hist.current_line
                result['line_move'] = round(line - hist.current_line, 1)
                
                hist.line_history.append(LineSnapshot(
                    timestamp=now,
                    line=line,
                    odds_over=odds_over,
                    odds_under=odds_under,
                ))
                hist.current_line = line
                
                logger.info(f"📊 LINE CHANGE [{event_name}] {player_name} {prop_type}: "
                           f"{result['old_line']} → {line} ({result['line_move']:+.1f})")
            
            # Check for odds change
            if abs(hist.current_odds_over - odds_over) > 0.01:
                result['odds_changed'] = True
                result['old_odds'] = hist.current_odds_over
                result['odds_swing'] = round(odds_over - hist.current_odds_over, 3)
                
                hist.odds_history.append(OddsSnapshot(
                    timestamp=now,
                    odds_over=odds_over,
                    odds_under=odds_under,
                ))
                
                logger.info(f"📈 ODDS CHANGE [{event_name}] {player_name} {prop_type} {line}: "
                           f"{result['old_odds']} → {odds_over} ({result['odds_swing']:+.3f})")
            
            hist.current_odds_over = odds_over
            hist.current_odds_under = odds_under
            hist.last_updated = now
            
        else:
            # New prop for this event
            result['is_new'] = True
            
            self.in_game[in_game_key] = InGameHistory(
                event_id=event_id,
                event_name=event_name,
                event_date=event_date,
                player_name=player_name,
                prop_type=prop_type,
                opening_line=line,
                opening_odds_over=odds_over,
                opening_odds_under=odds_under,
                opening_timestamp=now,
                current_line=line,
                current_odds_over=odds_over,
                current_odds_under=odds_under,
                last_updated=now,
            )
            
            logger.debug(f"🆕 NEW PROP [{event_name}] {player_name} {prop_type} {line} @ {odds_over}/{odds_under}")
        
        # === CROSS-GAME TRACKING ===
        if cross_game_key not in self.cross_game:
            self.cross_game[cross_game_key] = CrossGameHistory(
                player_name=player_name,
                prop_type=prop_type,
            )
        
        cross_hist = self.cross_game[cross_game_key]
        
        # Check if we already have this game
        existing_game = next(
            (g for g in cross_hist.games if g.event_id == event_id),
            None
        )
        
        if existing_game:
            # Update existing game entry
            existing_game.line = line
            existing_game.odds_over = odds_over
            existing_game.odds_under = odds_under
            existing_game.timestamp = now
        else:
            # Add new game to history
            cross_hist.games.append(PlayerGameLine(
                event_id=event_id,
                event_name=event_name,
                event_date=event_date,
                line=line,
                odds_over=odds_over,
                odds_under=odds_under,
                timestamp=now,
            ))
            
            # Check for line trend across games
            if len(cross_hist.games) >= 2:
                prev_game = sorted(cross_hist.games, key=lambda g: g.event_date)[-2]
                line_diff = line - prev_game.line
                if abs(line_diff) > 0.1:
                    logger.info(f"📉 CROSS-GAME LINE [{player_name}] {prop_type}: "
                               f"{prev_game.line} ({prev_game.event_name}) → {line} ({event_name}) "
                               f"({line_diff:+.1f})")
        
        return result
    
    def get_in_game_history(self, event_id: str, player_name: str = None) -> List[InGameHistory]:
        """Get in-game history for an event, optionally filtered by player."""
        results = []
        for key, hist in self.in_game.items():
            if key.startswith(f"{event_id}:"):
                if player_name is None or hist.player_name == player_name:
                    results.append(hist)
        return results
    
    def get_cross_game_history(self, player_name: str, prop_type: str = None) -> List[CrossGameHistory]:
        """Get cross-game history for a player."""
        results = []
        for key, hist in self.cross_game.items():
            if hist.player_name == player_name:
                if prop_type is None or hist.prop_type == prop_type:
                    results.append(hist)
        return results
    
    def get_biggest_movers(self, event_id: str, top_n: int = 10) -> Dict:
        """Get props with biggest movements for an event."""
        event_props = self.get_in_game_history(event_id)
        
        # By odds swing
        by_odds = sorted(event_props, key=lambda p: abs(p.odds_swing), reverse=True)
        
        # By line move
        by_line = sorted(event_props, key=lambda p: abs(p.line_move), reverse=True)
        
        return {
            'biggest_odds_swings': [
                {
                    'player': p.player_name,
                    'prop_type': p.prop_type,
                    'line': p.current_line,
                    'opening_odds': p.opening_odds_over,
                    'current_odds': p.current_odds_over,
                    'swing': p.odds_swing,
                    'num_changes': p.num_odds_changes,
                }
                for p in by_odds[:top_n] if p.odds_swing != 0
            ],
            'biggest_line_moves': [
                {
                    'player': p.player_name,
                    'prop_type': p.prop_type,
                    'opening_line': p.opening_line,
                    'current_line': p.current_line,
                    'move': p.line_move,
                    'num_changes': p.num_line_changes,
                }
                for p in by_line[:top_n] if p.line_move != 0
            ],
        }
    
    def get_player_line_trends(self, top_n: int = 20) -> List[Dict]:
        """Get players with biggest line trends across games."""
        trends = []
        for key, hist in self.cross_game.items():
            if len(hist.games) >= 2:
                trends.append({
                    'player_name': hist.player_name,
                    'prop_type': hist.prop_type,
                    'num_games': len(hist.games),
                    'average_line': hist.average_line,
                    'highest_line': hist.highest_line.line if hist.highest_line else None,
                    'lowest_line': hist.lowest_line.line if hist.lowest_line else None,
                    'trend': hist.line_trend,
                    'recent_games': [
                        {'event': g.event_name, 'line': g.line, 'date': g.event_date}
                        for g in sorted(hist.games, key=lambda x: x.event_date, reverse=True)[:5]
                    ]
                })
        
        return sorted(trends, key=lambda t: t['num_games'], reverse=True)[:top_n]
    
    def save_all(self) -> None:
        """Save all data."""
        # Get unique event IDs
        event_ids = set()
        for key in self.in_game.keys():
            event_id = key.split(':')[0]
            event_ids.add(event_id)
        
        for event_id in event_ids:
            self.save_event(event_id)
        
        self._save_cross_game_data()
        logger.info(f"Saved all data: {len(event_ids)} events, {len(self.cross_game)} player histories")

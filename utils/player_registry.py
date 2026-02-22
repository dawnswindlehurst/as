"""Player registry for name mapping and fuzzy matching."""
import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from difflib import SequenceMatcher
from config.settings import DATA_DIR
from utils.logger import log


class PlayerRegistry:
    """Registry for mapping player names across different sources.
    
    Provides fuzzy matching to handle name variations and maintain
    a cache of external player IDs.
    """
    
    def __init__(self, cache_file: Optional[Path] = None):
        """Initialize the player registry.
        
        Args:
            cache_file: Path to cache file (default: data/player_registry.json)
        """
        self.cache_file = cache_file or DATA_DIR / "player_registry.json"
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load player registry from cache file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
                log.info(f"Loaded {len(self.registry)} players from registry")
            except Exception as e:
                log.error(f"Failed to load player registry: {e}")
                self.registry = {}
        else:
            log.info("Player registry cache not found, starting fresh")
            self.registry = {}
    
    def save_registry(self):
        """Save player registry to cache file."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
            log.debug(f"Saved {len(self.registry)} players to registry")
        except Exception as e:
            log.error(f"Failed to save player registry: {e}")
    
    def add_player(self, name: str, external_id: str, sport: str, **metadata):
        """Add a player to the registry.
        
        Args:
            name: Player's full name
            external_id: External player ID
            sport: Sport (nba, soccer, tennis)
            **metadata: Additional player metadata (team, position, etc.)
        """
        normalized_name = self._normalize_name(name)
        
        if normalized_name not in self.registry:
            self.registry[normalized_name] = {
                "name": name,
                "external_id": external_id,
                "sport": sport,
                "aliases": [],
                **metadata
            }
            self.save_registry()
            log.info(f"Added player {name} ({external_id}) to registry")
        else:
            # Update existing entry
            self.registry[normalized_name].update({
                "external_id": external_id,
                "sport": sport,
                **metadata
            })
            self.save_registry()
            log.debug(f"Updated player {name} in registry")
    
    def get_player(self, name: str) -> Optional[Dict[str, Any]]:
        """Get player by exact name match.
        
        Args:
            name: Player name
            
        Returns:
            Player data dictionary or None
        """
        normalized_name = self._normalize_name(name)
        return self.registry.get(normalized_name)
    
    def get_external_id(self, name: str) -> Optional[str]:
        """Get external ID for a player.
        
        Args:
            name: Player name
            
        Returns:
            External player ID or None
        """
        player = self.get_player(name)
        return (
            player.get("external_id")
            if player else None
        )
    
    def find_player_fuzzy(self, name: str, sport: Optional[str] = None, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Find player using fuzzy name matching.
        
        Args:
            name: Player name to search for
            sport: Optional sport filter
            threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            Best matching player or None
        """
        normalized_search = self._normalize_name(name)
        best_match = None
        best_score = 0.0
        
        for player_key, player_data in self.registry.items():
            # Filter by sport if provided
            if sport and player_data.get("sport") != sport:
                continue
            
            # Calculate similarity
            score = self._similarity(normalized_search, player_key)
            
            # Check aliases too
            for alias in player_data.get("aliases", []):
                alias_score = self._similarity(normalized_search, self._normalize_name(alias))
                score = max(score, alias_score)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = player_data
        
        if best_match:
            log.debug(f"Fuzzy match for '{name}': {best_match['name']} (score: {best_score:.2f})")
        else:
            log.debug(f"No fuzzy match found for '{name}' (threshold: {threshold})")
        
        return best_match
    
    def add_alias(self, name: str, alias: str):
        """Add an alias for a player.
        
        Args:
            name: Player's primary name
            alias: Alternative name/spelling
        """
        normalized_name = self._normalize_name(name)
        
        if normalized_name in self.registry:
            aliases = self.registry[normalized_name].get("aliases", [])
            if alias not in aliases:
                aliases.append(alias)
                self.registry[normalized_name]["aliases"] = aliases
                self.save_registry()
                log.info(f"Added alias '{alias}' for player {name}")
        else:
            log.warning(f"Player {name} not found in registry, cannot add alias")
    
    def search_players(self, query: str, sport: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for players by name.
        
        Args:
            query: Search query
            sport: Optional sport filter
            limit: Maximum number of results
            
        Returns:
            List of matching players sorted by relevance
        """
        normalized_query = self._normalize_name(query)
        results = []
        
        for player_key, player_data in self.registry.items():
            # Filter by sport if provided
            if sport and player_data.get("sport") != sport:
                continue
            
            # Calculate similarity
            score = self._similarity(normalized_query, player_key)
            
            # Check name contains query
            if normalized_query in player_key:
                score = max(score, 0.9)
            
            # Check aliases
            for alias in player_data.get("aliases", []):
                alias_norm = self._normalize_name(alias)
                alias_score = self._similarity(normalized_query, alias_norm)
                if normalized_query in alias_norm:
                    alias_score = max(alias_score, 0.9)
                score = max(score, alias_score)
            
            if score > 0.5:  # Minimum threshold for search results
                results.append({
                    "score": score,
                    **player_data
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:limit]
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a player name for comparison.
        
        Args:
            name: Player name
            
        Returns:
            Normalized name (lowercase, no extra spaces)
        """
        return " ".join(name.lower().strip().split())
    
    def _similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def get_players_by_sport(self, sport: str) -> List[Dict[str, Any]]:
        """Get all players for a specific sport.
        
        Args:
            sport: Sport identifier (nba, soccer, tennis)
            
        Returns:
            List of players
        """
        return [
            player for player in self.registry.values()
            if player.get("sport") == sport
        ]
    
    def get_players_by_team(self, team: str, sport: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all players for a specific team.
        
        Args:
            team: Team name or abbreviation
            sport: Optional sport filter
            
        Returns:
            List of players
        """
        team_lower = team.lower()
        results = []
        
        for player in self.registry.values():
            if sport and player.get("sport") != sport:
                continue
            
            player_team = player.get("team", "").lower()
            if team_lower in player_team or player_team in team_lower:
                results.append(player)
        
        return results
    
    def clear_sport(self, sport: str):
        """Remove all players from a specific sport.
        
        Args:
            sport: Sport to clear
        """
        keys_to_remove = [
            key for key, player in self.registry.items()
            if player.get("sport") == sport
        ]
        
        for key in keys_to_remove:
            del self.registry[key]
        
        self.save_registry()
        log.info(f"Cleared {len(keys_to_remove)} players from {sport}")


# Global player registry instance
player_registry = PlayerRegistry()

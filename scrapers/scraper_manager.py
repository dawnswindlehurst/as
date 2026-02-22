"""Manager for all bookmaker scrapers."""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from scrapers.base_scraper import BaseScraper, OddsData
from scrapers.config import BOOKMAKERS_CONFIG, get_enabled_bookmakers
from utils.logger import log


class ScraperManager:
    """Manages all bookmaker scrapers and coordinates odds fetching."""
    
    def __init__(self):
        self._scrapers: Dict[str, BaseScraper] = {}
        self._enabled_scrapers: List[str] = []
    
    def register_scraper(self, scraper: BaseScraper):
        """Register a scraper instance.
        
        Args:
            scraper: Scraper instance to register
        """
        self._scrapers[scraper.name] = scraper
        if scraper.enabled:
            self._enabled_scrapers.append(scraper.name)
        log.info(f"Registered scraper: {scraper.name} (enabled={scraper.enabled})")
    
    def get_scraper(self, name: str) -> Optional[BaseScraper]:
        """Get a scraper by name.
        
        Args:
            name: Scraper name
            
        Returns:
            Scraper instance or None
        """
        return self._scrapers.get(name)
    
    def get_enabled_scrapers(self) -> List[BaseScraper]:
        """Get all enabled scrapers.
        
        Returns:
            List of enabled scraper instances
        """
        return [self._scrapers[name] for name in self._enabled_scrapers if name in self._scrapers]
    
    def has_scrapers(self) -> bool:
        """Check if any scrapers are registered.
        
        Returns:
            True if at least one scraper is registered, False otherwise
        """
        return len(self._scrapers) > 0
    
    def list_all_scrapers(self) -> Dict[str, Dict]:
        """List all scrapers with their status.
        
        Returns:
            Dictionary with scraper names and status info
        """
        result = {}
        for name, scraper in self._scrapers.items():
            config = BOOKMAKERS_CONFIG.get(name, {})
            result[name] = {
                "enabled": scraper.enabled,
                "type": scraper.integration_type.value,
                "category": scraper.bookmaker_type.value,
                "status": config.get("status", "active" if scraper.enabled else "disabled")
            }
        return result
    
    async def fetch_all_odds(self, game: str = None) -> Dict[str, List[OddsData]]:
        """Fetch odds from all enabled scrapers.
        
        Args:
            game: Optional game filter
            
        Returns:
            Dictionary mapping scraper name to list of odds
        """
        enabled = self.get_enabled_scrapers()
        
        if not enabled:
            log.warning("No enabled scrapers found")
            return {}
        
        log.info(f"Fetching odds from {len(enabled)} enabled scrapers")
        
        tasks = []
        scraper_names = []
        
        for scraper in enabled:
            tasks.append(scraper.get_esports_odds(game))
            scraper_names.append(scraper.name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        odds_by_scraper = {}
        for name, result in zip(scraper_names, results):
            if isinstance(result, Exception):
                log.error(f"Error fetching odds from {name}: {result}")
                odds_by_scraper[name] = []
            else:
                odds_by_scraper[name] = result
                log.info(f"Fetched {len(result)} odds from {name}")
        
        return odds_by_scraper
    
    async def compare_odds(self, game: str = None) -> List[Dict]:
        """Compare odds across all enabled scrapers.
        
        Args:
            game: Optional game filter
            
        Returns:
            List of odds comparisons
        """
        all_odds = await self.fetch_all_odds(game)
        
        # Group odds by event
        events_map = {}
        for bookmaker, odds_list in all_odds.items():
            for odds in odds_list:
                event_key = f"{odds.sport}_{odds.league}_{odds.team_home}_vs_{odds.team_away}"
                
                if event_key not in events_map:
                    events_map[event_key] = {
                        "event_name": odds.event_name,
                        "sport": odds.sport,
                        "league": odds.league,
                        "team_home": odds.team_home,
                        "team_away": odds.team_away,
                        "bookmakers": {}
                    }
                
                events_map[event_key]["bookmakers"][bookmaker] = {
                    "odds_home": odds.odds_home,
                    "odds_draw": odds.odds_draw,
                    "odds_away": odds.odds_away,
                    "timestamp": odds.timestamp
                }
        
        # Convert to list
        comparisons = []
        for event_key, event_data in events_map.items():
            if len(event_data["bookmakers"]) > 1:  # Only include events with multiple bookmakers
                # Calculate best odds (filter out None values)
                best_home = max(
                    (bm["odds_home"] for bm in event_data["bookmakers"].values() 
                     if bm["odds_home"] is not None),
                    default=0
                )
                best_away = max(
                    (bm["odds_away"] for bm in event_data["bookmakers"].values() 
                     if bm["odds_away"] is not None),
                    default=0
                )
                
                event_data["best_odds"] = {
                    "home": best_home,
                    "away": best_away
                }
                
                comparisons.append(event_data)
        
        log.info(f"Found {len(comparisons)} events with multiple bookmakers")
        return comparisons
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all scrapers.
        
        Returns:
            Dictionary mapping scraper name to health status
        """
        tasks = []
        scraper_names = []
        
        for name, scraper in self._scrapers.items():
            if scraper.enabled:
                tasks.append(scraper.health_check())
                scraper_names.append(name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_status = {}
        for name, result in zip(scraper_names, results):
            if isinstance(result, Exception):
                log.error(f"Health check failed for {name}: {result}")
                health_status[name] = False
            else:
                health_status[name] = result
                log.info(f"Health check for {name}: {'OK' if result else 'FAILED'}")
        
        return health_status


# Global scraper manager instance
scraper_manager = ScraperManager()

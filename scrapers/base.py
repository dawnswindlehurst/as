"""Base scraper class."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from utils.decorators import retry, log_errors


class ScraperBase(ABC):
    """Base class for all scrapers."""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    @retry(max_attempts=3)
    @log_errors
    def fetch_matches(self) -> List[Dict]:
        """Fetch upcoming matches.
        
        Returns:
            List of match dictionaries
        """
        pass
    
    @abstractmethod
    @retry(max_attempts=3)
    @log_errors
    def fetch_match_details(self, match_id: str) -> Optional[Dict]:
        """Fetch details for a specific match.
        
        Args:
            match_id: Match identifier
            
        Returns:
            Match details dictionary
        """
        pass

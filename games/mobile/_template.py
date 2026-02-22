"""Template for mobile game implementations.

To add a new mobile game:
1. Copy this template
2. Rename the class
3. Implement all abstract methods
4. The registry will auto-discover it
"""
from typing import Dict, List, Optional
from games.base import GameBase


class MobileGameTemplate(GameBase):
    """Template for mobile game implementation.
    
    This is a template and should not be instantiated.
    """
    
    def __init__(self):
        super().__init__()
        self.category = "mobile"
        self.has_maps = False
        self.has_draft = False
        self.data_source = "TBD"
    
    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming matches.
        
        Returns:
            List of match dictionaries
        """
        raise NotImplementedError("Template should not be used directly")
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get match details.
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details dictionary
        """
        raise NotImplementedError("Template should not be used directly")
    
    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get team statistics.
        
        Args:
            team_name: Team name
            
        Returns:
            Team statistics
        """
        raise NotImplementedError("Template should not be used directly")

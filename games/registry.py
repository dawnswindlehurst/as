"""Game registry - auto-discovery and registration."""
import importlib
import pkgutil
from typing import Dict, List, Type, Optional
from utils.logger import log
from games.base import GameBase


class GameRegistry:
    """Registry for all game implementations.
    
    Automatically discovers and registers all game classes.
    """
    
    def __init__(self):
        self._games: Dict[str, Type[GameBase]] = {}
        self._instances: Dict[str, GameBase] = {}
    
    def register(self, game_class: Type[GameBase]):
        """Register a game class.
        
        Args:
            game_class: Game class to register
        """
        name = game_class.__name__
        self._games[name] = game_class
        log.debug(f"Registered game: {name}")
    
    def get(self, name: str) -> Optional[GameBase]:
        """Get a game instance by name.
        
        Args:
            name: Game name
            
        Returns:
            Game instance or None
        """
        if name not in self._instances:
            if name in self._games:
                self._instances[name] = self._games[name]()
            else:
                log.warning(f"Game not found: {name}")
                return None
        
        return self._instances[name]
    
    def get_all(self) -> List[GameBase]:
        """Get all registered game instances.
        
        Returns:
            List of game instances
        """
        return [self.get(name) for name in self._games.keys()]
    
    def get_pc_games(self) -> List[GameBase]:
        """Get all PC game instances.
        
        Returns:
            List of PC game instances
        """
        return [g for g in self.get_all() if g.category == "pc"]
    
    def get_mobile_games(self) -> List[GameBase]:
        """Get all mobile game instances.
        
        Returns:
            List of mobile game instances
        """
        return [g for g in self.get_all() if g.category == "mobile"]
    
    def list_names(self) -> List[str]:
        """List all registered game names.
        
        Returns:
            List of game names
        """
        return list(self._games.keys())
    
    def auto_discover(self):
        """Auto-discover and register all game implementations."""
        # Import PC games
        try:
            import games.pc as pc_pkg
            self._discover_in_package(pc_pkg)
        except ImportError:
            log.warning("PC games package not found")
        
        # Import mobile games
        try:
            import games.mobile as mobile_pkg
            self._discover_in_package(mobile_pkg)
        except ImportError:
            log.warning("Mobile games package not found")
        
        log.info(f"Auto-discovered {len(self._games)} games")
    
    def _discover_in_package(self, package):
        """Discover games in a package.
        
        Args:
            package: Package to search
        """
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            if not ispkg and not modname.startswith('_'):
                try:
                    module = importlib.import_module(f"{package.__name__}.{modname}")
                    
                    # Find all classes that inherit from GameBase
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, GameBase) and 
                            attr is not GameBase):
                            self.register(attr)
                            
                except Exception as e:
                    log.error(f"Error importing {modname}: {e}")


# Global registry instance
game_registry = GameRegistry()

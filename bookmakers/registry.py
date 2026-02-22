"""Bookmaker registry - auto-discovery and registration."""
import importlib
import pkgutil
from typing import Dict, List, Type, Optional
from utils.logger import log
from bookmakers.base import BookmakerBase


class BookmakerRegistry:
    """Registry for all bookmaker implementations.
    
    Automatically discovers and registers all bookmaker classes.
    """
    
    def __init__(self):
        self._bookmakers: Dict[str, Type[BookmakerBase]] = {}
        self._instances: Dict[str, BookmakerBase] = {}
    
    def register(self, bookmaker_class: Type[BookmakerBase]):
        """Register a bookmaker class.
        
        Args:
            bookmaker_class: Bookmaker class to register
        """
        name = bookmaker_class.__name__
        self._bookmakers[name] = bookmaker_class
        log.debug(f"Registered bookmaker: {name}")
    
    def get(self, name: str) -> Optional[BookmakerBase]:
        """Get a bookmaker instance by name.
        
        Args:
            name: Bookmaker name
            
        Returns:
            Bookmaker instance or None
        """
        if name not in self._instances:
            if name in self._bookmakers:
                self._instances[name] = self._bookmakers[name]()
            else:
                log.warning(f"Bookmaker not found: {name}")
                return None
        
        return self._instances[name]
    
    def get_all(self) -> List[BookmakerBase]:
        """Get all registered bookmaker instances.
        
        Returns:
            List of bookmaker instances
        """
        return [self.get(name) for name in self._bookmakers.keys()]
    
    def get_traditional(self) -> List[BookmakerBase]:
        """Get all traditional bookmaker instances.
        
        Returns:
            List of traditional bookmaker instances
        """
        return [b for b in self.get_all() if b.type == "traditional"]
    
    def get_crypto(self) -> List[BookmakerBase]:
        """Get all crypto bookmaker instances.
        
        Returns:
            List of crypto bookmaker instances
        """
        return [b for b in self.get_all() if b.type == "crypto"]
    
    def list_names(self) -> List[str]:
        """List all registered bookmaker names.
        
        Returns:
            List of bookmaker names
        """
        return list(self._bookmakers.keys())
    
    def auto_discover(self):
        """Auto-discover and register all bookmaker implementations."""
        # Import traditional bookmakers
        try:
            import bookmakers.traditional as traditional_pkg
            self._discover_in_package(traditional_pkg)
        except ImportError:
            log.warning("Traditional bookmakers package not found")
        
        # Import crypto bookmakers
        try:
            import bookmakers.crypto as crypto_pkg
            self._discover_in_package(crypto_pkg)
        except ImportError:
            log.warning("Crypto bookmakers package not found")
        
        log.info(f"Auto-discovered {len(self._bookmakers)} bookmakers")
    
    def _discover_in_package(self, package):
        """Discover bookmakers in a package.
        
        Args:
            package: Package to search
        """
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            if not ispkg and not modname.startswith('_'):
                try:
                    module = importlib.import_module(f"{package.__name__}.{modname}")
                    
                    # Find all classes that inherit from BookmakerBase
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BookmakerBase) and 
                            attr is not BookmakerBase):
                            self.register(attr)
                            
                except Exception as e:
                    log.error(f"Error importing {modname}: {e}")


# Global registry instance
bookmaker_registry = BookmakerRegistry()

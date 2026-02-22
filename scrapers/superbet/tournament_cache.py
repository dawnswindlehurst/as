"""Tournament cache with TTL for Superbet API."""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from threading import Lock


@dataclass
class CacheEntry:
    """Represents a cache entry with TTL."""
    
    data: Any
    timestamp: float
    ttl: int  # seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl


class TournamentCache:
    """Thread-safe cache for tournament data with TTL."""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize tournament cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                return entry.data
            elif entry:
                # Remove expired entry
                del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            self._cache[key] = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
    
    def invalidate(self, key: str):
        """
        Invalidate (remove) a cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        """Remove all expired entries from cache."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for entry in self._cache.values() if entry.is_expired())
            return {
                'total_entries': total,
                'expired_entries': expired,
                'active_entries': total - expired,
            }

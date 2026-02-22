"""Generic caching utilities with TTL support."""

import time
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from threading import Lock
from functools import wraps


@dataclass
class CacheEntry:
    """Represents a cache entry with TTL."""
    
    data: Any
    timestamp: float
    ttl: int  # seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl


class TTLCache:
    """Thread-safe cache with Time-To-Live support."""
    
    def __init__(self, default_ttl: int = 3600, max_size: Optional[int] = None):
        """
        Initialize TTL cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            max_size: Maximum cache size (None for unlimited)
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
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
                self._hits += 1
                return entry.data
            elif entry:
                # Remove expired entry
                del self._cache[key]
                self._misses += 1
            else:
                self._misses += 1
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
            # Check max size and evict oldest if needed
            if self.max_size and len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].timestamp)
                del self._cache[oldest_key]
            
            self._cache[key] = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
    
    def delete(self, key: str):
        """
        Delete a cache entry.
        
        Args:
            key: Cache key to delete
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def cleanup_expired(self):
        """Remove all expired entries from cache."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for entry in self._cache.values() if entry.is_expired())
            hit_rate = self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0
            
            return {
                'total_entries': total,
                'expired_entries': expired,
                'active_entries': total - expired,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
            }


def cached(ttl: int = 3600, cache_instance: Optional[TTLCache] = None):
    """
    Decorator to cache function results with TTL.
    
    Args:
        ttl: Time-to-live in seconds
        cache_instance: TTLCache instance to use (creates new if None)
    
    Example:
        @cached(ttl=300)
        def expensive_function(arg1, arg2):
            # ... expensive computation ...
            return result
    """
    _cache = cache_instance or TTLCache(default_ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        # Attach cache instance for manual control
        wrapper.cache = _cache
        return wrapper
    
    return decorator

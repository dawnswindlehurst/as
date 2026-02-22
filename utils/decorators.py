"""Decorators for common functionality."""
import time
import functools
from typing import Callable, Any
from utils.logger import log


def timer(func: Callable) -> Callable:
    """Decorator to time function execution.
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log.info(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        log.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    log.warning(f"{func.__name__} attempt {attempts} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


def log_errors(func: Callable) -> Callable:
    """Decorator to log errors without raising.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(f"Error in {func.__name__}: {e}", exc_info=True)
            return None
    return wrapper


def cache_result(ttl_seconds: int = 300):
    """Decorator to cache function results.
    
    Args:
        ttl_seconds: Time to live for cache in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from args and kwargs
            key = str(args) + str(kwargs)
            
            # Check if cached and not expired
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    log.debug(f"Using cached result for {func.__name__}")
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator

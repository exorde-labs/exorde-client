
import functools
import time

def cached(duration):
    """
    A decorator that caches the result of a function for a specified duration.

    Usage:
    @cached(duration_in_seconds)
    def my_function(args):
        ...

    Parameters:
    - duration (int): The duration for which the result of the function should 
                        be cached in seconds.

    Returns:
    - function: A decorated function that caches its results.

    Example:
    @cached(5 * 60)  # Cache results for 5 minutes
    def add(a, b):
        return a + b

    # The first call to add(2, 3) will calculate the result (5) and cache it.
    # Subsequent calls within the next 5 minutes will return the cached result.
    result = add(2, 3)
    """
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            
            # Check if the result is cached and not expired
            if key in cache and time.time() - cache[key]['timestamp'] < duration:
                return cache[key]['result']
            
            # Calculate and cache the result
            result = await func(*args, **kwargs)
            cache[key] = {
                'result': result,
                'timestamp': time.time(),
            }
            return result
        
        return wrapper
    
    return decorator

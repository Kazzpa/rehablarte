from functools import wraps
from loguru import logger
import time
import inspect


def log_duration(func_name=None):
    """Log execution time for any async/sync function"""

    def decorator(func):
        # ✅ Capture func_name BEFORE defining wrapper
        display_name = func_name or func.__name__

        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                logger.info(f"{display_name}: {duration:.2f}s ✅")
                return result
            except Exception as e:
                duration = time.perf_counter() - start_time
                logger.error(f"{display_name}: {duration:.2f}s ❌ {str(e)}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                logger.info(f"{display_name}: {duration:.2f}s ✅")
                return result
            except Exception as e:
                duration = time.perf_counter() - start_time
                logger.error(f"{display_name}: {duration:.2f}s ❌ {str(e)}")
                raise

        # Return correct wrapper
        return wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator

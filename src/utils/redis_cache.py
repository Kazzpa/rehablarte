from modules.redis_db import redis_client
from loguru import logger
import inspect
import redis
import pickle


async def cached_api_call(cache_key: str, api_function, *args, ttl=600, **kwargs):
    # Try to get from cache
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info("Loading cached result")
            return pickle.loads(cached)
    except (redis.RedisError, pickle.UnpicklingError) as e:
        logger.warning(f"Cache retrieval failed for {cache_key}: {e}")

    # Execute API call - check if async or sync
    if inspect.iscoroutinefunction(api_function):
        result = await api_function(*args, **kwargs)  # Async function
    else:
        result = api_function(*args, **kwargs)  # Sync function

    # Store in Redis with expiration
    if ttl > 0:
        await redis_client.setex(cache_key, ttl, pickle.dumps(result))
    # Save forever
    else:
        await redis_client.set(cache_key, pickle.dumps(result))
    return result

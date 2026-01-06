from modules.redis_db import redis_storage
from loguru import logger
import redis
import pickle


async def cached_api_call(cache_key, api_function, *args, **kwargs):
    # Try to get from cache
    try:
        cached = redis_storage.get_data(cache_key)
        if cached:
            logger.info("Loading cached result")
            return pickle.loads(cached)
    except (redis.RedisError, pickle.UnpicklingError) as e:
        logger.warning(f"Cache retrieval failed for {cache_key}: {e}")
    # Execute API call
    result = await api_function(*args, **kwargs)

    # Store in Redis with expiration
    redis_storage.set_data(cache_key, pickle.dumps(result))
    return result

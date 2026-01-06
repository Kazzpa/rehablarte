from modules.redis_db import redis_client
from loguru import logger
import redis
import pickle

def cached_api_call(cache_key, api_function, *args, ttl=600, **kwargs):
    # Try to get from cache
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Loading cached result")
            return pickle.loads(cached)
    except (redis.RedisError, pickle.UnpicklingError) as e:
        logger.warning(f"Cache retrieval failed for {cache_key}: {e}")
    # Execute API call
    result = api_function(*args, **kwargs)

    # Store in Redis with expiration
    if ttl > 0 :
        redis_client.setex(cache_key, ttl, pickle.dumps(result))
    # Save forever
    else:
        redis_client.set(cache_key, pickle.dumps(result))
    return result


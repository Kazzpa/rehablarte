from modules.redis_db import redis_client
from loguru import logger
import json
import inspect
import redis
import pickle


async def cached_api_call(cache_key: str, api_function, *args, ttl=600, result_type=None, **kwargs):
    # Try to get from cache
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info("Loading cached result")
            data = json.loads(cached)
            if result_type:
                return result_type.model_validate(data)
            return data
    except (redis.RedisError, json.JSONDecodeError) as e:
        logger.warning(f"Cache retrieval failed for {cache_key}: {e}")

    # Execute API call - check if async or sync
    if inspect.iscoroutinefunction(api_function):
        result = await api_function(*args, **kwargs)  # Async function
    else:
        result = api_function(*args, **kwargs)  # Sync function

    # Serialize based on what result is
    if hasattr(result, "model_dump"):
         # Pydantic model
        serialized = json.dumps(result.model_dump(mode="json")) 
    elif isinstance(result, (dict, list, str)):
        # plain types
        serialized = json.dumps(result)
    elif isinstance(result, bytes):
        # bytes
        try:
            serialized = result.decode("utf-8")  # try as JSON text first
        except UnicodeDecodeError:
            # Binary data (audio, images etc) — use pickle instead
            if ttl > 0:
                await redis_client.setex(cache_key, ttl, pickle.dumps(result))
            else:
                await redis_client.set(cache_key, pickle.dumps(result))
        return result               
    else:
        raise TypeError(f"Cannot serialize result of type {type(result)}")

    # Store in Redis with expiration
    if ttl > 0:
        await redis_client.setex(cache_key, ttl, serialized)
    # Save forever
    else:
        await redis_client.set(cache_key, serialized)
    return result

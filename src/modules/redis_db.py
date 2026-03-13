from redis import asyncio as aioredis
from aiogram.fsm.storage.redis import RedisStorage
import redis
from loguru import logger
from os import getenv
from dotenv import load_dotenv
from decorators import log_duration

load_dotenv()


@log_duration("Redis: Init")
def create_redis_client() -> redis.Redis:
    redis_host = getenv("REDIS_HOST")
    redis_port = getenv("REDIS_PORT", 6379)
    redis_password = getenv("REDIS_PASSWORD")
    client = aioredis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=0,  # The default Redis database index
    )
    logger.info("Connected to redis")
    return client


redis_client = create_redis_client()

# Storage to manage memory session
storage = RedisStorage(redis=redis_client)

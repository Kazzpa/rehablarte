import redis
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger
from os import getenv
from dotenv import load_dotenv

load_dotenv()


def create_redis_storage() -> RedisStorage:
    redis_host = getenv("REDIS_HOST")
    redis_port = getenv("REDIS_PORT", 6379)
    redis_password = getenv("REDIS_PASSWORD")
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=0,  # The default Redis database index
    )
    redis_storage = RedisStorage(redis=redis_client, data_ttl=600)
    logger.info("Connected to redis")
    return redis_storage


redis_storage = create_redis_storage()
from loguru import logger
from errors.errors import RehablarteRedisException
from models.palabra_entity import (
    PalabraSimple,
    Palabra
)
from utils.redis_repository import RedisRepository, RePalabraRepository
from modules.redis_db import redis_client


async def getPalabra(word: str) -> Palabra | PalabraSimple | None:
    logger.info("Getting palabra from database")
    redis_repo = RedisRepository(redis_client)
    palara_repo = RePalabraRepository(redis_repo)
    data = await palara_repo.get(word=word)
    if (data is None):
        logger.warning("Palabra not found for that word")
        return
    elif (isinstance(data, Palabra)):
        logger.info("Palabra type is complete type")
        return Palabra.model_validate_json(data)
    elif (isinstance(data, PalabraSimple)):
        logger.info("Palabra type is simple")
        return PalabraSimple.model_validate_json(data)
    else:
        logger.error("Type not expected mapping the model of Palabra")
        raise RehablarteRedisException("Type not expected from redis db")


async def savePalabra(palabra: PalabraSimple | Palabra) -> None:
    logger.info("Saving palabra to database")
    redis_repo = RedisRepository(redis_client)
    palabra_repo = RePalabraRepository(redis_repo)
    await palabra_repo.save(palabra=palabra)

async def savePalabraTemp(palabra: PalabraSimple | PalabraSimple) -> None:
    logger.info("Saving palabra temp to database")
    redis_repo = RedisRepository(redis_client)
    palabra_repo = RePalabraRepository(redis_repo)
    await palabra_repo.save_temp(palabra=palabra)
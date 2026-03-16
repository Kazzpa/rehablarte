# rae api cache keys
from datetime import datetime
from aiogram import Bot
from loguru import logger

from api.api_rae import get_rae_random, get_rae_word
from errors.errors import ReHablarteMappingException
from models.palabra_entity import Palabra, PalabraSimple
from utils.redis_cache import cached_api_call
from models.chat_entity import ReChatSession


class cache_keys_prefix:
    rae_random_key = "RAERANDOM"
    rae_word_key = "RAEWORD:"
    rae_tts_key = "TTS:"


# function to calculate seconds until midnight
def seconds_until_midnight() -> int:
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Move to next midnight
    from datetime import timedelta

    midnight += timedelta(days=1)
    return int((midnight - now).total_seconds())

# function to send daily word
async def sendDailyWord(session: ReChatSession, bot: Bot):
    logger.info("Sending daily word...")
    res_type = PalabraSimple
    function_cb = get_rae_random
    # Comprobar configuracion
    if session.chat.diariaConfig.senses | session.chat.diariaConfig.origin:
        res_type = Palabra
        function_cb = get_rae_word

    # comprobar si la palabra diaria se ha guardado ya
    cache_key = cache_keys_prefix.rae_random_key

    rae_data = await cached_api_call(
        cache_key=cache_key,
        api_function=function_cb,
        ttl=seconds_until_midnight(),  # Cache for until midnight
        result_type=res_type,
    )

    if not isinstance(rae_data, PalabraSimple | Palabra):
        raise ReHablarteMappingException(
            "Error mapping the type of the object after api call"
        )

    palabro = rae_data.word
    await bot.send_message(session.chat.id, f"El palabro de hoy es: {palabro}")
    # TODO: Add support for origen y significado

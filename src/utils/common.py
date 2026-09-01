# rae api cache keys
from datetime import datetime
from aiogram import Bot
from httpcore import Origin
from loguru import logger

from api.api_rae import get_rae_daily, get_rae_word
from errors.errors import ReHablarteMappingException
from models.palabra_entity import Palabra, PalabraSimple, Sense
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
    function_cb = get_rae_daily
    # Comprobar configuracion
    if session.chat.diariaConfig.senses | session.chat.diariaConfig.origin:
        res_type = Palabra
        function_cb = get_rae_word

    # comprobar si la palabra diaria se ha guardado ya
    cache_key = cache_keys_prefix.rae_word_key
#TODO: Bug here, we need to change the save method, we need to check the type of the word
    rae_data = await cached_api_call(
        cache_key=cache_key,
        api_function=function_cb,
        ttl=seconds_until_midnight(),  # Cache for until midnight
        result_type=res_type,
    )

    origin = None
    senses = None
    if not isinstance(rae_data, (PalabraSimple, Palabra)):
        raise ReHablarteMappingException(
            "Error mapping the type of the object after api call"
        )
    elif isinstance(rae_data, Palabra):
        origin = rae_data.origin
        senses = rae_data.sensesList

    palabro = rae_data.word
    mensaje = palabraStrBuilder(palabro, origin, senses)

    await bot.send_message(session.chat.id,  mensaje)


def palabraStrBuilder(word: str, origin: Origin, senses: list[Sense]) -> str:
    """
    Util function to build a message to send with the sense and origin of a word

    :param word: string with the word
    :param origin: Origin object
    :param Senses: List with the senses of the word
    :return mesaje: String lines with either full description or just the word
    """
    logger.info("Building full word description message")
    lines: list[str] = []
    lines.append(f"El palabro de hoy es: {word}")
    # De momento damos un soporte sinple para origen y sinonimos
    if (origin is not None):
        lines.append(f"El origen del palabro de hoy es: {origin.raw}")
    if (senses is not None and senses.count() > 0):
        for sense in senses:
            if sense.description is not None:
                lines.append(f"El significado del palabro de hoy es: {sense.description}")
            if sense.synonyms:
                lines.append(f"Los sinonimos son:\n" + "\n".join(sense.synonyms))
            if sense.antonyms:
                lines.append(f"Los antonimos son:\n" + "\n".join(sense.antonyms))

    mensaje = "\n".join(lines)
    return mensaje
    
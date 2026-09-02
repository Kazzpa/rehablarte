# rae api cache keys
from datetime import datetime
from aiogram import Bot
from httpcore import Origin
from loguru import logger

from api.api_rae import get_rae_daily, get_rae_word
from models.palabra_entity import Palabra, PalabraSimple, Sense
from utils.redis_cache import cached_api_call
from utils.palabra import getPalabra, savePalabraTemp
from models.chat_entity import ReChatDiariaConfig, ReChatSession
from utils.session import update_session


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
    config: ReChatDiariaConfig = session.chat.diariaConfig
    # Comprobar configuracion
    if config.senses or config.origin:
        res_type = Palabra

    # check if we have the word already
    if config.last_palabra is not None:
        word: Palabra | PalabraSimple | None = await getPalabra(config.last_palabra)
    else:
        word = None

    if word is None:
        # call the api
        word: PalabraSimple = await get_rae_daily()
        if res_type is Palabra:
            word: Palabra = await get_rae_word(word.word)

        # save the word
        await savePalabraTemp(word)
        config.last_palabra = word.word
        # update session
        session.is_dirty = True
        await update_session(session)
        
    
    mensaje = palabraStrBuilder(word.word, getattr(word, "origin", None), getattr(word, "sensesList", None))
    await bot.send_message(session.chat.id, mensaje)


def palabraStrBuilder(word: str, origin: Origin | None, senses: list[Sense] | None) -> str:
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
    if (senses is not None and len(senses) > 0):
        for sense in senses:
            if sense.description is not None:
                lines.append(f"El significado del palabro de hoy es: {sense.description}")
            if sense.synonyms:
                lines.append(f"Los sinonimos son:\n" + "\n".join(sense.synonyms))
            if sense.antonyms:
                lines.append(f"Los antonimos son:\n" + "\n".join(sense.antonyms))

    mensaje = "\n".join(lines)
    return mensaje
    
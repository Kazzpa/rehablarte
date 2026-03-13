import os
from loguru import logger
from aiogram import types, Router, F
from aiogram.types import Message
from decorators import log_duration
from modules.tts import PiperTTS
from modules.stt import SpeechToText
from utils.redis_cache import cached_api_call

# Router capturing all commands
response_handler = Router()

MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    raise ValueError("MODEL_PATH not found in .env file!")

tts = PiperTTS(model_path=MODEL_PATH)
stt = SpeechToText()


# All handlers should be attached to the Router (or Dispatcher)
@response_handler.message(F.text)
@log_duration("Text handler")
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    logger.info("Executing reply handler")
    text = message.text
    if text:
        logger.info("Message is type text")
    else:
        return
    status_msg = await message.answer("⏳ Generando audio...")

    cache_key = f"TTS:{text.lower().strip()}"

    audio_bytes = await cached_api_call(
        cache_key=cache_key,
        api_function=tts.get_audio_bytes,
        text=text,
        ttl=3600,  # Cache for 1 hour
    )
    title_generated = message.from_user.first_name or "Usuario" + " generado"
    await message.bot.send_audio(
        chat_id=message.chat.id,
        audio=types.input_file.BufferedInputFile(
            file=audio_bytes, filename="response.mp3"
        ),
        title=title_generated,
        performer="RehablarTe Bot",
        caption=f"🎵 {text[:50]}...",
    )

    await message.bot.delete_message(
        chat_id=message.chat.id, message_id=status_msg.message_id
    )


@response_handler.message(F.audio | F.voice)
@log_duration("Audio_files handler")
async def audio_file_handler(message: Message) -> None:
    logger.info("Executing audio files handler")
    audio = message.audio
    voice = message.voice
    audio_object = None
    if audio:
        logger.info("Message is type Audio")
        audio_object = audio
    elif voice:
        logger.info("Message is type Voice")
        audio_object = audio

    status_msg = await message.answer("⏳ Transcribiendo audio...")
    audio_file = await message.bot.get_file(audio_object.file_id)
    audio_path = audio_file.file_path
    download_path = audio_path.split("/")[-1]
    await message.bot.download_file(audio_path, download_path)
    transcribed_text = await stt.transcribe(audio_path=download_path)
    # Remove downloaded_audio
    os.remove(download_path)
    await message.bot.delete_message(
        chat_id=message.chat.id, message_id=status_msg.message_id
    )

    await message.answer(transcribed_text)


@response_handler.message()
async def handle_unknown_content(message: Message):
    await message.answer(
        f"Hola, {message.from_user.full_name}!, estoy esperando un mensaje de texto o audio"
    )

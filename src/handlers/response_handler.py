import os
from loguru import logger
from aiogram import types, Router
from aiogram.types import Message
from decorators import log_duration
from modules.tts import PiperTTS
from utils.redis_cache import cached_api_call
# Router capturing all commands
response_handler = Router()

MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    raise ValueError("MODEL_PATH not found in .env file!")

tts = PiperTTS(model_path=MODEL_PATH)
# All handlers should be attached to the Router (or Dispatcher)
@response_handler.message()
@log_duration("TTS_Process")
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    logger.info("Executing TTS-Process")
    # Send a copy of the received message
    text = message.text
    if not text:
        await message.answer(
            f"Hola, {message.from_user.full_name}!, estoy esperando un mensaje de texto"
        )

    status_msg = await message.answer("⏳ Generando audio...")
    cache_key=f"TTS:{text}"

    audio_bytes = cached_api_call(
        cache_key=cache_key,
        api_function=tts.get_audio_bytes,
        text=text,
        ttl=3600  # Cache for 1 hour
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

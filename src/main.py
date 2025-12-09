import asyncio
import logging
import sys
import os
from os import getenv
from aiogram import Bot, Dispatcher,types, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from tts import PiperTTS
from dotenv import load_dotenv
from decorators import log_duration
load_dotenv()  # Auto-loads .env
# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file!")

# Bot defined globally (accessible to all handlers)
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

MODEL_PATH = os.getenv("MODEL_PATH")
if not MODEL_PATH:
    raise ValueError("MODEL_PATH not found in .env file!")

tts = PiperTTS(model_path=MODEL_PATH)
# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
router = Router()
dp.include_router(router)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hola, {html.bold(message.from_user.full_name)}!")


@router.message()
@log_duration("TTS_Process")
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        text = message.text
        if not text:
            await message.answer(f"Hola, {message.from_user.full_name}!, estoy esperando un mensaje de texto")

        status_msg = await message.answer("⏳ Generando audio...")
        audio_bytes = tts.get_audio_bytes(text)
        title_generated = message.from_user.first_name or "Usuario" + " generado"
        await bot.send_audio(
            chat_id=message.chat.id,
            audio=types.input_file.BufferedInputFile(
                file=audio_bytes,
                filename="response.mp3"
            ),
            title=title_generated,
            performer="RehablarTe Bot",
            caption=f"🎵 {text[:50]}..."
        )


        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Ha habido un problema🥲")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
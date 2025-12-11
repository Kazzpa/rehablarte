from loguru import logger
from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from decorators import log_duration

# Router capturing all commands
member_commands = Router()

@member_commands.message(CommandStart())
# TODO: Change this to modify the status of the bot
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    logger.info("Calling start command")
    await message.answer(f"Hola, {html.bold(message.from_user.full_name)}!")

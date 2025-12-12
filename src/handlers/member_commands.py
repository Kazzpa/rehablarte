from loguru import logger
from aiogram import html, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from decorators import log_duration
from api.api_rae import get_rae_random

# Router capturing all commands
member_commands = Router()

@member_commands.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    logger.info("Calling start command")
    await message.answer(f"Hola, {html.bold(message.from_user.full_name)}!")

@member_commands.message(Command("aleatoria"))
async def command_random_handler(message: Message) -> None:
    """
    This function handles the command to get a random word from RAE API
    this function should call a middleware to call the api
    :param message: Description
    :type message: Message
    """
    logger.info("Calling random comand")
    rae_data = await get_rae_random()
    palabro = rae_data["word"]
    await message.answer(f"Toma palabro aleatorio: {palabro}")
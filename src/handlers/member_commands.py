from loguru import logger
from aiogram import html, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from api.api_rae import get_rae_random

# this function set ups the help text in commands
# Add here more commands
async def setup_bot_commands(bot: Bot):
    """
    function to set up bot commands help text, call only once
    add below new commands
    
    :param bot: Description
    :type bot: Bot
    """
    logger.info("Setting up bot commands")
    commands = [
        BotCommand(command = "start", description = "Commando para iniciar el bot"),
        BotCommand(command = "help", description = "Comando de ayuda del bot"),
        BotCommand(command = "aleatoria", description = "Este comando devuelve una palabra aleatoria de la RAE")
    ]
    await bot.set_my_commands(commands)


# Router capturing all commands
member_commands = Router()

@member_commands.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This command should start the bot
    """
    logger.info("Calling start command")
    await message.answer(f"Hola, {html.bold(message.from_user.full_name)}!")


@member_commands.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    Command to reply with bot functionallities
    Add explanation here with each functionality
    
    :param message: Description
    :type message: Message
    """
    logger.info("Calling help command")
    a = """
        Para obtener un audio de un texto tan solo mandame el audio.
        - /start: Iniciar bot.
        - /help: Comando para mostar este mensaje
        """
    await message.answer(a)

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
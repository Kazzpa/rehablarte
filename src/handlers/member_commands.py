from loguru import logger
from aiogram import html, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from api.api_rae import get_rae_random, get_rae_word


# Group state for waiting on rae api
class RaeState(StatesGroup):
    searchWord = State()


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
        BotCommand(command="start", description="Commando para iniciar el bot"),
        BotCommand(command="help", description="Comando de ayuda del bot"),
        BotCommand(
            command="aleatoria",
            description="Este comando devuelve una palabra aleatoria de la RAE",
        ),
        BotCommand(
            command="palabra",
            description="Busca el significado de una palabra en la RAE",
        ),
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
    helpText = """
        Para obtener un audio de un texto tan solo mandame el audio.
        - /start: Iniciar bot.
        - /help: Comando para mostar este mensaje
        """
    await message.answer(helpText)


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


@member_commands.message(Command("palabra"))
async def command_get_word(message: Message, state: FSMContext) -> None:
    """
    This function is the first step in FSM Context(event) and command for getting a palabra from RAE API
    """
    logger.info("Asking user for a word")
    # Set the next state to waiting
    await state.set_state(RaeState.searchWord)
    await message.answer("¿Que palabra quieres buscar en la RAE?")
    logger.info("Waiting for user's input...")


@member_commands.message(RaeState.searchWord)
async def process_word(message: Message, state: FSMContext) -> None:
    """
    This function is the second step in FSM context(event) for getting a word from RAE API
    """
    logger.info("updating state with user's input")
    await state.update_data(word=message.text)
    await state.set_state(RaeState.searchWord)
    await message.answer("Espera le estoy preguntando a Reverte")
    word = message.text
    logger.info(f"Searching for word '{word}' in API")
    rae_data = await get_rae_word(word)
    if not rae_data:
        logger.error("Error calling rae api")
        raise Exception("Error calling rae api for word")
    # TODO: Move this to constant
    if rae_data == "NOT_FOUND":
        logger.warning("Word not found in rae api")
        await message.answer(f"No se ha encontrado la palara {word}")
        # Break flow here
        return
    # From here we parse the result and reply with desired text
    meanings = rae_data["meanings"]

    # TODO: De momento devolvemos el primer significado
    # Expandir esto en el futuro
    # TODO: Implement DTO and mapping here
    senses = meanings[0]["senses"]
    result = senses[0]["description"]
    await message.answer(f"El significado de {word} es {result}")

import asyncio
import logging
import sys
from loguru import logger
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from handlers.member_commands import member_commands, setup_bot_commands
from handlers.response_handler import response_handler
from handlers.errors_handler import errors_router
from handlers.event_handler import event_router
from handlers.middlewares import InitializeSessionMiddleware
from modules.redis_db import storage
from handlers.conversation_handler import daily_config_router

load_dotenv()  # Auto-loads .env

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file!")

# Bot defined globally (accessible to all handlers)
bot = None

# Configure dispatcher and set up commands/middlewares | We set the storage sesssion as well
dp = Dispatcher(storage=storage)
# Error hanlder must be before
dp.include_router(errors_router)
# routers
dp.include_router(member_commands)
dp.include_router(daily_config_router)
dp.include_router(response_handler)
dp.include_router(event_router)
# middlewares
dp.update.middleware(InitializeSessionMiddleware(bot=bot))
dp.startup.register(setup_bot_commands)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    global bot
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("Starting bot!")

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

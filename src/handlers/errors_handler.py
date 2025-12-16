from loguru import logger
from aiogram import Router
from aiogram.types import Update, ErrorEvent

# Define a router to capture all exceptions
errors_router = Router()

"""
This handler will manage all global errors, for specific behaviours or custom exception add try/catch in command/event
"""


@errors_router.errors()
async def errors_handler(event: ErrorEvent):
    update: Update = event.update
    ex: Exception = event.exception
    cause = getattr(ex, "__cause__", None)
    if cause:
        logger.error(f"Error ocurred: {cause}")
    else:
        logger.error(f"Internal Error - unkown cause {ex}")
    try:
        if update.message:
            await update.message.answer("❌ Ocurrió un error interno.")
    except Exception as send_error:
        logger.warning(f"Failed to send error message: {send_error}")

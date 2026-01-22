from loguru import logger
from aiogram import BaseMiddleware
from aiogram.types.chat import Chat
from aiogram.fsm.context import FSMContext
from utils.session import initialize_session


class InitializeSessionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logger.info("In initialization middleware")
        # get fsm context from data
        state: FSMContext = data["state"]

        # get the chat from data
        chat: Chat = data.get("event_chat")

        await initialize_session(state, chat)

        return await handler(event, data)

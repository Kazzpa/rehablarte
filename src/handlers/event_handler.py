from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from loguru import logger
from models.chat_entity import ReChat, ReChatSession
from utils.redis_repository import RedisRepository, ReChatRepository
from modules.redis_db import redis_client
from utils.session import get_session, update_session

event_router = Router()
redis_repo = RedisRepository(redis_client)

# Manage bot/users joining a chat group or leaving a chat group
@event_router.my_chat_member()
async def chat_group_member_event(event: ChatMemberUpdated, state: FSMContext):
    logger.info("User leaving/joining detected")

    chat_id = event.chat.id
    user = event.new_chat_member.user

    if event.chat.type == "private":
        logger.warning("This functionality is not available for private chats")
        # TODO: Maybe save new private chat here
        return

    # load repository
    chat_repo = ReChatRepository(redis_repo)

    # Get current session
    session = await get_session(state)
    re_chat = session.chat

    # If current chat is not found in db then create new and save it
    if re_chat is None:
        logger.info("Session does not have a chat saved, searching db...")
        re_chat = await chat_repo.get(chat_id=chat_id)
        if not re_chat:
            logger.info("Chat not found in DB, creating new chat...")
            re_chat = ReChat(id=chat_id, active=False, chat_members=[], type="group")
            await chat_repo.save(re_chat)

        session.chat = ReChatSession(re_chat)
        session.initialized = True

    # If we have a session check initialize status
    if not session.initialized:
        re_chat = session.chat

        session.initialized = True
        session.chat = re_chat
        await state.update_data(session)

    # Check type of user
    if user.is_bot:
        # TODO: Initialize session for bot
        logger.info("User is bot skipping...")
        return

    

    # Check if user is leaving/joining
        # to check new joined
        # check new_chat_member status is member & old is left or other maybe
        # to check someone left or kicked
        # check new is left old is member

    # Update DB creating/deleting corresponding info


    id = event.chat.id
    new_chat = ReChat(id)

    chat_repo = ReChatRepository(redis_repo)
    logger.info(new_chat)
    await chat_repo.save(new_chat)


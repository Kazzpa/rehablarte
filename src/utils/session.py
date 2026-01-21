from loguru import logger
from aiogram.fsm.context import FSMContext
from aiogram.types.chat import Chat
from models.chat_entity import ReChatSession, ReChat, RePrivateChat, ReChatGroup
from datetime import datetime
from utils.redis_repository import ReSessionRepository, RedisRepository
from modules.redis_db import redis_client

async def get_session(state: FSMContext) -> ReChatSession:
    logger.info("Getting session")
    data = await state.get_data()
    rawSession = data.get("chat_session")
    if rawSession is None:
        logger.info("No session detected, creating session...")
        return ReChatSession()
     
    return ReChatSession.model_validate(rawSession)

async def update_session(state: FSMContext, session: ReChatSession):
    logger.info("Updating session...")
    await state.update_data(chat_session=session.model_dump())

async def initialize_session(state: FSMContext, chat: Chat):
    logger.info("Initializing session")
    data = await state.get_data()
    rawSession = data.get("chat_session")
    if rawSession is not None:
        logger.info("Session alredy initialized, cancelling...")
        return
    chat_id = chat.id
    chat_type = chat.type
    username = chat.username

    if chat_type is None:
        logger.info("Initialize empty chat")
        chat = ReChat(id=chat_id, firstInteraction=datetime.now())
    elif chat_type == "private":
        logger.info("Initializing session as private")
        if username is None:
            logger.error("Error username in a private chat cannot be None")
            raise Exception("Error username is None")
        chat = RePrivateChat(id=chat_id, firstInteraction=datetime.now(), username=username)
    elif chat_type in ["group", "supergroup"]:
        logger.info("Initializing session as group chat")
        chat = ReChatGroup(id=chat_id, firstInteraction=datetime.now(), chat_members=[], type=chat_type)
    new_session = ReChatSession(initialized=True, chat=chat)
    await update_session(state=state, session=new_session)

    # TODO: REMOVE THIS; ONLY TESTING
    redis_repo = RedisRepository(redis_client)
    session_repo = ReSessionRepository(redis_repo)
    session_repo.save(new_session)
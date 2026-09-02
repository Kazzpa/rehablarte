from loguru import logger
from aiogram.types.chat import Chat
from errors.errors import RehablarteInternalException
from models.chat_entity import (
    ReChatSession,
    ReChat,
    RePrivateChat,
    ReChatGroup,
    ReChatMember,
)
from datetime import datetime
from utils.redis_repository import ReSessionRepository, RedisRepository
from modules.redis_db import redis_client


# This function should return a member from the session chat, it assumes you already got the session and chat
async def get_member_from_chat(
    chat: ReChatGroup, idOrUsername: str
) -> ReChatMember | None:
    logger.info("Searching member in session")
    member_list = chat.chat_members
    return next(
        filter(
            lambda member: member.id == idOrUsername | member.username == idOrUsername,
            member_list,
        )
    )

# Return a session
async def get_session(chat_id: int) -> ReChatSession:
    logger.info("Getting session")
    redis_repo = RedisRepository(redis_client)
    session_repo = ReSessionRepository(redis_repo)
    data = await session_repo.get(chat_id=chat_id)
    if data is None:
        logger.info("No session detected, creating session...")
        return ReChatSession()

    return ReChatSession.model_validate_json(data)

# Function to save the session always, whether is dirty or not
async def save_session(session: ReChatSession):
    logger.info("Saving session...")
    redis_repo = RedisRepository(redis_client)
    session_repo = ReSessionRepository(redis_repo)
    await session_repo.save(session=session)

# Function to update dirty session, it expects a dirty session
async def update_session(session: ReChatSession) -> None:
    if session is None:
        raise RehablarteInternalException("Error - Session is not initialized")

    logger.info(f"Persisting session {session.chat.id} to DB")
    await save_session(session=session)
    session.is_dirty = False


# Factory method to create sessions
async def initialize_new_session(chat: Chat) -> ReChatSession:
    logger.info("Initializing new session")

    chat_id = chat.id
    chat_type = chat.type
    username = chat.username

    if chat_type is None:
        logger.info("Initialize empty chat")
        new_chat = ReChat(id=chat_id, firstInteraction=datetime.now())
    elif chat_type == "private":
        logger.info("Initializing session as private")
        if username is None:
            raise RehablarteInternalException(
                "Error username in a private chat cannot be None"
            )
        new_chat = RePrivateChat(
            id=chat_id, firstInteraction=datetime.now().date(), username=username
        )
    elif chat_type in ["group", "supergroup"]:
        logger.info("Initializing session as group chat")
        new_chat = ReChatGroup(
            id=chat_id,
            firstInteraction=datetime.now().date(),
            chat_members=[],
            type=chat_type,
        )
    return ReChatSession(initialized=True, chat=new_chat)

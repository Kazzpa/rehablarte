from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from loguru import logger
from datetime import datetime
from models.chat_entity import ReChatGroup, ReChatMember
from utils.redis_repository import RedisRepository
from modules.redis_db import redis_client
from utils.session import (
    get_session,
    get_member_from_chat,
    update_session,
    check_session_persistance,
)

event_router = Router()
redis_repo = RedisRepository(redis_client)


# Manage bot/users joining a chat group or leaving a chat group
@event_router.my_chat_member()
async def chat_group_member_event(
    event: ChatMemberUpdated, state: FSMContext, bot: Bot
):
    logger.info("User leaving/joining detected")

    chat = event.chat
    user = event.new_chat_member.user

    if user.is_bot and user.id == bot.id:
        logger.info("User affected is self - Rehablarte Bot - Skipping")
        return

    if chat.type == "private":
        logger.warning("This functionality is not available for private chats")
        return

    session = await get_session(state)
    session_chat: ReChatGroup = session.chat
    new_status = event.new_chat_member.status

    # Check if user is leaving/joining
    # TODO: Check if is necessary to check admin status
    # new user
    if new_status == "member":
        logger.info("New user detected")
        new_member = await get_member_from_chat(chat, user.id)
        # Si no existia lo creamos
        if new_member is None:
            new_member = ReChatMember(
                id=user.id,
                username=user.username,
                status=new_status,
                joinedAt=datetime.now().date(),
                isBot=user.is_bot,
            )
        # Actualizamos estado y guardamos
        else:
            new_member.status = new_status

    # user leaving
    elif event.new_chat_member.status in ["left", "kicked"]:
        logger.info("User leaving group detected")
        # Search for user in db and delete it
        old_member = await get_member_from_chat(chat, user.id)
        # if user is not in db skip
        if old_member is None:
            logger.warning("The user was not found when trying to delete")
            return

        session_chat.chat_members.remove(old_member)

    # Update session & set to dirty
    await update_session(state=state, session=session)
    session.is_dirty = True
    # Save changes into persistance
    await check_session_persistance(state=state)

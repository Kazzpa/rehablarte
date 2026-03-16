from loguru import logger
from aiogram import BaseMiddleware, Bot
from aiogram.types.chat import Chat
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.member_commands import get_daily_word
from models.chat_entity import ReChatSession
from modules.redis_db import redis_client
from utils.common import sendDailyWord
from utils.redis_repository import RedisRepository, ReSessionRepository
from utils.session import initialize_new_session


class InitializeSessionMiddleware(BaseMiddleware):
    def __init__(self, bot):
        self.bot = bot
        self.redis_repo = RedisRepository(redis_client)
        self.session_repo = ReSessionRepository(self.redis_repo)

    async def __call__(self, handler, event, data):
        logger.info("In initialization middleware")
        # get chat directly from conversation data
        chat: Chat = data["event_chat"]

        if chat is None:
            logger.error("No chat found in event!")
            return await handler(event, data)

        # now search for persistance data
        session = await self.session_repo.get(chat_id=chat.id)

        if session is None:
            logger.warning(f"No session found for chat {chat.id}, creating new one...")
            session = await initialize_new_session(chat)
            await self.session_repo.save(session=session)

        # Set cronjob here for daily word
        sendDailyWordCronjob(session=session, bot=self.bot)

        # Inject session into handler directly
        data["session"] = session

        result = await handler(event, data)

        # persist session back if dirty
        if session.is_dirty:
            logger.info(f"Persisting dirty session for chat {chat.id}")
            await self.session_repo.save(session)
            session.is_dirty = False

        return result

def sendDailyWordCronjob(bot: Bot, session: ReChatSession):
    if not(session.chat.diariaConfig.isActive):
        logger.info("Daily word not active")
        return
    
    timeToSend = session.chat.diariaConfig.scheduleTime
    logger.info(f"Daily word is active, setting cronjob for time: {timeToSend}...")
    # Configure cronjob
    cronjob = AsyncIOScheduler()
    cronjob.add_job(sendDailyWord, "cron", hour=timeToSend, minute=0, kwargs={"session": session, "bot": bot})
    cronjob.start()
from loguru import logger
from aiogram import BaseMiddleware, Bot
from aiogram.types.chat import Chat
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from errors.errors import RehablarteInternalException
from handlers.member_commands import get_daily_word
from models.chat_entity import ReChatDiariaConfig, ReChatSession
from modules.redis_db import redis_client
from utils.common import sendDailyWord
from utils.redis_repository import RedisRepository, ReSessionRepository
from utils.session import initialize_new_session
from tzlocal import get_localzone_name


class InitializeSessionMiddleware(BaseMiddleware):
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.redis_repo = RedisRepository(redis_client)
        self.session_repo = ReSessionRepository(self.redis_repo)
        self.cronjob = scheduler

    # TODO: look for away to reduce middleware execution times
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
        if self.cronjob is not None:
            sendDailyWordCronjob(session=session, bot=self.bot, cronjob=self.cronjob)
        else:
            logger.warning("Could not set up daily word cronjob, sheduler is None")

        # Inject session into handler directly
        data["session"] = session

        result = await handler(event, data)

        # persist session back if dirty
        if session.is_dirty:
            logger.info(f"Persisting dirty session for chat {chat.id}")
            await self.session_repo.save(session)
            session.is_dirty = False

        return result


def sendDailyWordCronjob(bot: Bot, session: ReChatSession, cronjob: AsyncIOScheduler):
    if session.chat.diariaConfig is None:
        logger.error("Config not found")
        raise RehablarteInternalException("Error setting daily word - config not found")

    # get session cronjob config
    config: ReChatDiariaConfig = session.chat.diariaConfig
    time_to_send = config.scheduleTime

    # TODO: check again logic behind the cronjob
    if config.cronjob_id is None:
        logger.warning("creating jobId")
        config.cronjob_id = f"daily_word:{session.chat.id}"
    else:
        job = cronjob.get_job(config.cronjob_id)
        if job is not None:
            logger.warning("Cronjob is already created")
            if job.next_run_time is not None:
                hour = job.next_run_time.hour
                minute = job.next_run_time.minute
                if hour == time_to_send.hour and minute == time_to_send.minute:
                    return

    if not (config.isActive):
        logger.info("Daily word not active")
        if cronjob.get_job(config.cronjob_id):
            cronjob.remove_job(config.cronjob_id)
        return

    cronjob.add_job(
        sendDailyWord,
        trigger="cron",
        id=config.cronjob_id,
        replace_existing=True,
        hour=time_to_send.hour,
        minute=time_to_send.minute,
        timezone=get_localzone_name(),
        kwargs={"session": session, "bot": bot},
        misfire_grace_time=300,
    )

    logger.info(
        f"Daily word is active, setting cronjob for time: {time_to_send.isoformat}..."
    )

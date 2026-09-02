import json
from errors.errors import RehablarteRedisException
from models.chat_entity import ReChat, ReChatSession
from models.palabra_entity import Palabra, PalabraSimple


class RedisRepository:
    def __init__(self, redis):
        self.redis = redis

    async def save(self, key: str, data: dict):
        await self.redis.set(key, json.dumps(data))

    async def save_temp(self, key: str, data: dict, ttl: int = 86400):
        await self.redis.setex(key, ttl, json.dumps(data))

    async def get(self, key: str) -> dict | None:
        raw = await self.redis.get(key)
        return json.loads(raw) if raw else None

    async def delete(self, key: str):
        await self.redis.delete(key)


class ReSessionRepository:
    def __init__(self, repo: RedisRepository):
        self.repo = repo

    def _key(self, chat_id: int) -> str:
        return f"session_chat_id:{chat_id}"

    async def save(self, session: ReChatSession):
        await self.repo.save(
            self._key(session.chat.id), session.model_dump(mode="json")
        )

    async def get(self, chat_id: int) -> ReChatSession | None:
        data = await self.repo.get(self._key(chat_id))
        return ReChatSession.model_validate(data) if data else None


class ReChatRepository:
    def __init__(self, repo: RedisRepository):
        self.repo = repo

    def _key(self, chat_id: int) -> str:
        return f"Chat_id:{chat_id}"

    async def save(self, chat: ReChat):
        await self.repo.save(self._key(chat.id), chat.model_dump(mode="json"))

    async def get(self, chat_id: int) -> ReChat | None:
        data = await self.repo.get(self._key(chat_id))
        return ReChat.model_validate(data) if data else None


class RePalabraRepository:
    def __init__(self, repo: RedisRepository):
        self.repo = repo

    def _key(self, raw: str) -> str:
        return f"raw:{raw}"

    async def save(self, palabra: Palabra | PalabraSimple):
        await self.repo.save(self._key(palabra.word), palabra.model_dump(mode="json"))

    # Save only 24h
    async def save_temp(self, palabra: Palabra | PalabraSimple):
        await self.repo.save_temp(self._key(palabra.word), palabra.model_dump(mode="json"), 86400)

    async def get(self, word: str) -> Palabra | PalabraSimple | None:
        data = await self.repo.get(self._key(word))
        if isinstance(data, Palabra):
            return Palabra.model_validate(data) if data else None
        elif isinstance(data, PalabraSimple):
            return PalabraSimple.model_validate(data) if data else None
        else:
            raise RehablarteRedisException(f"Exception searching for palabra in redis db with word {word}")
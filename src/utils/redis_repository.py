import json
from models.chat_entity import ReChat, ReChatSession


class RedisRepository:
    def __init__(self, redis):
        self.redis = redis

    async def save(self, key: str, data: dict):
        await self.redis.set(key, json.dumps(data))

    async def get(self, key: str) -> dict | None:
        raw = await self.redis.get(key)
        return json.loads(raw) if raw else None

    async def delete(self, key: str):
        await self.redis.delete(key)

class ReSessionRepository:
    def __init__(self, repo: RedisRepository):
        self.repo = repo
    
    def _key(self, chat_id: int) -> str:
        return f"Session Chat id:{chat_id}"
    
    async def save(self, session: ReChatSession):
        await self.repo.save(self._key(session.chat.id), session.__dict__)

    async def get(self, chat_id: int) -> ReChatSession | None:
        data = await self.repo.get(self._key(chat_id))
        return ReChat(**data) if data else None
    


class ReChatRepository:
    def __init__(self, repo: RedisRepository):
        self.repo = repo

    def _key(self, chat_id: int) -> str:
        return f"Chat:{chat_id}"

    async def save(self, chat: ReChat):
        await self.repo.save(self._key(chat.id), chat.__dict__)

    async def get(self, chat_id: int) -> ReChat | None:
        data = await self.repo.get(self._key(chat_id))
        return ReChat(**data) if data else None

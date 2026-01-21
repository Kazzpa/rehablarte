from pydantic import BaseModel
from typing import Literal, List
from datetime import datetime

class ReChat(BaseModel):
    id: int
    firstInteraction: datetime

# Representation of private chat
class RePrivateChat(ReChat):
    username: str

# Representation of group chat users
class ReChatMembers(BaseModel):
    id: int
    username: str
    status: Literal["creator", "administrator", "member", "restricted", "left", "kicked"] # TODO: Maybe move this to a global so it can be reused in the future?
    joinedAt: datetime

# Representation of group chat
class ReChatGroup(ReChat):
    active: bool = False
    chat_members: List[ReChatMembers]
    type: Literal["group", "supergroup"]

# Representation of a session
class ReChatSession(BaseModel):
    initialized: bool = False
    chat: ReChat | None = None

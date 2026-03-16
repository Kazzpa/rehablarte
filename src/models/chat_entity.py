from pydantic import BaseModel, Field
from typing import Literal, Union
from datetime import datetime, time


# Representation of a diaria word configuration
class ReChatDiariaConfig(BaseModel):
    isActive: bool
    repetition: int = 0  # 0 No repetition
    scheduleTime: time  # hour of the day to send the message
    senses: bool = False  # Whether the bot should display the meaning of the word
    origin: bool = False  # Whether the bot should display the origin of the word


# Representation of group chat users
class ReChatMember(BaseModel):
    id: int
    username: str
    status: Literal[
        "creator", "administrator", "member", "restricted", "left", "kicked"
    ]  # TODO: Maybe move this to a global so it can be reused in the future?
    joinedAt: datetime
    is_bot: bool = False  # Use this attribute to ignore text from other bots


class ReChat(BaseModel):
    id: int
    firstInteraction: datetime
    kind: Literal["base", "private", "group"] = "base"
    diariaConfig: ReChatDiariaConfig = ReChatDiariaConfig(
        isActive=False,
        origin=False,
        senses=False,
        scheduleTime=time(hour=17, minute=48),  # hora coño
        repetition=0,
    )


# Representation of private chat
class RePrivateChat(ReChat):
    username: str
    kind: Literal["private"] = "private"


# Representation of group chat
class ReChatGroup(ReChat):
    kind: Literal["group"] = "group"
    active: bool = False
    chat_members: list[ReChatMember]
    type: Literal["group", "supergroup"]


# Set up union
ChatUnion = Union[RePrivateChat, ReChatGroup]


# Representation of a session
class ReChatSession(BaseModel):
    initialized: bool = False
    chat: ChatUnion | None = None

    # Internal field to track if session needs persistence
    is_dirty: bool = Field(default=False, exclude=True)

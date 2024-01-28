from __future__ import annotations

import random

from enum import StrEnum, auto
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class EntityNotFoundError(Exception):
    pass


class ChannelNotFoundError(EntityNotFoundError):
    pass


class UserNotFoundError(EntityNotFoundError):
    pass


class MessageType(StrEnum):
    SYSTEM = auto()
    USER = auto()


class SystemMessage(BaseModel):
    type: Annotated[
        Literal[MessageType.SYSTEM],
        Field(default=MessageType.SYSTEM)
    ]

    content: str

    @classmethod
    def user_joined(cls, user_name: str) -> SystemMessage:
        content = f"{user_name} has joined the channel."

        return cls(content=content)
    
    @classmethod
    def user_left(cls, user_name: str) -> SystemMessage:
        content = f"{user_name} has left the channel."

        return cls(content=content)


class UserMessage(BaseModel):
    type: Annotated[
        Literal[MessageType.USER],
        Field(default=MessageType.USER)
    ]

    sender_name: str
    sender_color_id: int
    content: str


Message = Annotated[
    Union[SystemMessage, UserMessage],
    Field(discriminator="type")
]


class User(BaseModel):
    name: str
    color_id: int

    @classmethod
    def from_name(cls, name: str) -> User:
        return cls(name=name, color_id=random.randrange(255))


class Channel(BaseModel):
    name: str
    users: dict[str, User]
    messages: list[UserMessage]

    def append_message(self, message: UserMessage) -> Channel:
        messages = [*self.messages, message]

        return self.model_copy(
            update={
                "messages": messages
            }
        )

    def append_user(self, user: User) -> Channel:
        users = self.users.copy()
        users[user.name] = user

        return self.model_copy(
            update={
                "users": users
            }
        )
    
    def remove_user(self, user_name: str) -> Channel:
        if not user_name in self.users:
            raise EntityNotFoundError
        
        users = self.users.copy()
        del users[user_name]

        return self.model_copy(
            update={
                "users": users
            }
        )

    @classmethod
    def from_name(cls, name: str) -> Channel:
        return cls(
            name=name,
            users={},
            messages=[]
        )


class App(BaseModel):
    channels: dict[str, Channel]

    def del_channel(self, name: str) -> App:
        if not self.channels.get(name):
            raise ChannelNotFoundError
        
        channels = self.channels.copy()
        del channels[name]

        return self.model_copy(
            update={
                "channels": channels
            }
        )

    def get_channel(self, name: str) -> Channel:
        channel = self.channels.get(name)

        if not channel:
            raise ChannelNotFoundError

        return channel

    def set_channel(self, name: str, channel: Channel) -> App:
        channels = self.channels.copy()
        channels[name] = channel

        return self.model_copy(
            update={
                "channels": channels
            }
        )

    @classmethod
    def empty(cls) -> App:
        return cls(channels={})

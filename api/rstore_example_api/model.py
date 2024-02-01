from __future__ import annotations

import random

from enum import StrEnum, auto
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class AccessError(Exception):
    pass


class DuplicateEntityError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass


class ChannelNotFoundError(EntityNotFoundError):
    pass


class DuplicateUserError(DuplicateEntityError):
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


class UserMessageData(BaseModel):
    content: str


Message = Annotated[
    Union[SystemMessage, UserMessage],
    Field(discriminator="type")
]


class UserData(BaseModel):
    session_id: str
    name: str
    channel_name: str


class User(BaseModel):
    session_id: str
    name: str
    channel_name: str
    color_id: Annotated[
        int,
        Field(default_factory=lambda: random.randrange(255))
    ]


class Channel(BaseModel):
    name: str
    users: Annotated[dict[str, User], Field(default_factory=dict)]
    messages: Annotated[list[UserMessage], Field(default_factory=list)]

    def append_message(self, message: UserMessage) -> Channel:
        messages = [*self.messages, message]

        return self.copy(update={"messages": messages})

    def del_user(self, user_name: str) -> Channel:
        if user_name not in self.users:
            raise UserNotFoundError

        users = self.users.copy()
        del users[user_name]

        return self.copy(update={"users": users})

    def get_user(self, user_name: str) -> User:
        if user_name not in self.users:
            raise UserNotFoundError

        return self.users[user_name]

    def set_user(self, user_name, user: User) -> Channel:
        users = self.users.copy()
        users[user_name] = user

        return self.copy(update={"users": users})


class AppState(BaseModel):
    channels: dict[str, Channel]
    users: dict[str, User]

    def add_message(self, channel_name: str, message: Message) -> AppState:
        channel = self.get_channel(channel_name)
        channel = channel.append_message(message)

        channels = self.channels.copy()
        channels[channel_name] = channel

        return self.copy(update={"channels": channels})

    def add_user(self, data: UserData) -> AppState:
        if data.session_id in self.users:
            raise DuplicateUserError

        if data.channel_name in self.channels:
            channel = self.channels[data.channel_name]

            if data.name in channel.users:
                raise DuplicateUserError
        else:
            channel = Channel(name=data.channel_name)

        user = User(**data.dict())
        channel = channel.set_user(data.name, user)

        channels = self.channels.copy()
        channels[data.channel_name] = channel

        users = self.users.copy()
        users[data.session_id] = user

        return AppState(channels=channels, users=users)

    def get_channel(self, name: str) -> Channel:
        if name not in self.channels:
            raise ChannelNotFoundError

        return self.channels[name]

    def get_user(self, session_id: str) -> User:
        if session_id not in self.users:
            raise UserNotFoundError

        return self.users[session_id]

    def remove_user(self, session_id: str) -> AppState:
        user = self.get_user(session_id)
        users = self.users.copy()
        del users[session_id]

        channel = self.channels[user.channel_name]
        channel = channel.del_user(user.name)

        if not channel.users:
            channels = self.channels.copy()
            del channels[user.channel_name]
        else:
            channels = self.channels

        return AppState(channels=channels, users=users)

    @classmethod
    def empty(cls) -> AppState:
        return cls(channels={}, users={})

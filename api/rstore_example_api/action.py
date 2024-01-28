from enum import StrEnum, auto
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from .model import Message, UserData


class ActionType(StrEnum):
    ADD_MESSAGE = auto()
    ADD_USER = auto()
    REMOVE_USER = auto()


class AddMessageAction(BaseModel):
    type: Annotated[
        Literal[ActionType.ADD_MESSAGE],
        Field(default=ActionType.ADD_MESSAGE)
    ]

    channel_name: str
    message: Message


class AddUserAction(BaseModel):
    type: Annotated[
        Literal[ActionType.ADD_USER],
        Field(default=ActionType.ADD_USER)
    ]

    data: UserData


class RemoveUserAction(BaseModel):
    type: Annotated[
        Literal[ActionType.REMOVE_USER],
        Field(default=ActionType.REMOVE_USER)
    ]

    data: UserData


AppAction = Annotated[
    Union[
        AddMessageAction,
        AddUserAction,
        RemoveUserAction
    ],
    Field(discriminator="type")
]

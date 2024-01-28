import asyncio

from rstore import Dispatch, Store

from .model import App, Message, SystemMessage
from .action import AppAction, AddMessageAction, AddUserAction, RemoveUserAction


async def _send_message(
    store: Store[App, AppAction],
    channel_name: str,
    message: Message
) -> None:
    app = await store.get_state()

    if channel_name not in app.channels:
        return

    await store.dispatch(
        AddMessageAction(
            channel_name=channel_name,
            message=message
        )
    )


async def system_message_middleware(
    store: Store[App, AppAction],
    next: Dispatch,
    action: AppAction
) -> App:
    message: Message
    result = await next(action)

    match action:
        case AddUserAction(channel_name=channel_name, user_name=user_name):
            message = SystemMessage.user_joined(user_name)

        case RemoveUserAction(channel_name=channel_name, user_name=user_name):
            message = SystemMessage.user_left(user_name)

        case _:
            return result
    
    asyncio.create_task(_send_message(channel_name, message))
    return result

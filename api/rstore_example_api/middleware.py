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
    result = await next(action)

    match action:
        case AddUserAction(data=data):
            channel_name = data.channel_name
            message = SystemMessage.user_joined(data.name)

        case RemoveUserAction(data=data):
            channel_name = data.channel_name
            message = SystemMessage.user_left(data.name)

        case _:
            return result

    asyncio.create_task(_send_message(store, channel_name, message))
    return result

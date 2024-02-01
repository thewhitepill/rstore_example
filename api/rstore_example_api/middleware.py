from rstore import Dispatch, Store

from .action import AppAction, AddMessageAction, AddUserAction, RemoveUserAction
from .model import AppState, Message, SystemMessage
from .task import run_task


async def _send_message(
    store: Store[AppState, AppAction],
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
    store: Store[AppState, AppAction],
    next: Dispatch,
    action: AppAction
) -> AppState:
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

    run_task(_send_message(store, channel_name, message))

    return result

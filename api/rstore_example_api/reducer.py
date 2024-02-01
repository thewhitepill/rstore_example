from .action import (
    AppAction,
    AddMessageAction,
    AddUserAction,
    RemoveUserAction
)

from .model import AppState


def app_reducer(state: AppState, action: AppAction) -> AppState:
    match action:
        case AddMessageAction(channel_name=channel_name, message=message):
            return state.add_message(channel_name, message)

        case AddUserAction(data=data):
            return state.add_user(data)

        case RemoveUserAction(data=data):
            return state.remove_user(data.session_id)

        case _:
            raise TypeError(f"Unknown action: {action.type}")

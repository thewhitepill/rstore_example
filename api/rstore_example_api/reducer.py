from .action import (
    AppAction,
    AddMessageAction,
    AddUserAction,
    RemoveUserAction
)

from .model import App


def app_reducer(app: App, action: AppAction) -> App:
    match action:
        case AddMessageAction(channel_name=channel_name, message=message):
            return app.add_message(channel_name, message)

        case AddUserAction(data=data):
            return app.add_user(data)

        case RemoveUserAction(data=data):
            return app.remove_user(data.session_id)

        case _:
            raise TypeError(f"Unknown action: {action.type}")

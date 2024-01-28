from .action import (
    AppAction,
    AddMessageAction,
    AddUserAction,
    RemoveUserAction
)

from .model import App, Channel, User


def _handle_add_message_action(app: App, action: AddMessageAction) -> App:
    channel_name = action.channel_name
    message = action.message

    channel = app \
        .get_channel(channel_name) \
        .append_message(message)

    return app.set_channel(channel_name, channel)


def _handle_add_user_action(app: App, action: AddUserAction) -> App:
    channel_name = action.channel_name
    user_name = action.user_name

    user = User.from_name(user_name)
    channel = app.get_channel(channel_name) \
        if channel_name in app.channels else Channel.from_name(channel_name)

    channel = channel.append_user(user)

    return app.set_channel(channel_name, channel)


def _handle_remove_user_action(app: App, action: RemoveUserAction) -> App:
    channel_name = action.channel_name
    user_name = action.user_name

    channel = app \
        .get_channel(channel_name) \
        .remove_user(user_name)

    if not channel.users:
        return app.del_channel(channel_name)

    return app.set_channel(channel_name, channel)


def app_reducer(app: App, action: AppAction) -> App:
    match action:
        case AddMessageAction():
            return _handle_add_message_action(app, action)

        case AddUserAction():
            return _handle_add_user_action(app, action)

        case RemoveUserAction():
            return _handle_remove_user_action(app, action)

        case _:
            raise TypeError(f"Unknown action: {action.type}")

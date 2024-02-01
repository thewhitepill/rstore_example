import redis.asyncio
import rstore
import secrets

from typing import Annotated, Optional

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Response,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware

from .action import AddMessageAction, AddUserAction, AppAction, RemoveUserAction
from .config import config
from .middleware import system_message_middleware
from .model import (
    AccessError,
    AppState,
    Channel,
    Message,
    UserData,
    UserMessage,
    UserMessageData,
    UserNotFoundError
)

from .reducer import app_reducer
from .task import run_task


redis_client = redis.asyncio.from_url(config.redis.url)
store = rstore.create_store(
    app_reducer,
    initial_state_factory=AppState.empty,
    middleware=[
        system_message_middleware
    ]
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


websockets = {}


def get_session_id(
    session_id: Annotated[Optional[str], Cookie()] = None
) -> str:
    if not session_id:
        raise AccessError

    return session_id


SessionId = Annotated[str, Depends(get_session_id)]


async def broadcast_message(channel_name: str, message: Message) -> None:
    state = await store.get_state()
    channel = state.get_channel(channel_name)

    for user in channel.users.values():
        websocket = websockets.get(user.session_id)

        if not websocket:
            continue

        await websocket.send_json(message)


def message_broadcaster(action: AppAction, state: AppState) -> None:
    if not isinstance(action, AddMessageAction):
        return

    run_task(broadcast_message(action.channel_name, action.message))


store.subscribe(message_broadcaster)


@app.on_event("startup")
async def handle_startup() -> None:
    await redis_client.ping()
    await store.bind(redis_client)


@app.on_event("shutdown")
async def handle_shutdown() -> None:
    await store.unbind()
    await redis_client.close()


@app.websocket("/ws")
async def connect(websocket: WebSocket, session_id: SessionId) -> None:
    await websocket.accept()

    websockets[session_id] = websocket

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del websockets[session_id]

        state = await store.get_state()

        if session_id not in state.users:
            return

        user = state.users[session_id]
        data = UserData(**user.dict())
        action = RemoveUserAction(data)

        await store.dispatch(action)


@app.post("/session")
async def register(response: Response) -> dict:
    session_id = secrets.token_hex(32)

    response.set_cookie("session_id", session_id, httponly=True)

    return {}


@app.post("/channel/{channel_name}/user/{user_name}")
async def join_channel(
    channel_name: str,
    user_name: str,
    session_id: SessionId
) -> Channel:
    data = UserData(
        session_id=session_id,
        name=user_name,
        channel_name=channel_name
    )

    action = AddUserAction(data)
    state = await store.dispatch(action)
    channel = state.channels[channel_name]

    return channel


@app.post("/channel/{channel_name}/message")
async def send_message(
    channel_name: str,
    data: UserMessageData,
    session_id: SessionId
) -> dict:
    state = await store.get_state()

    user_by_session_id = state.get_user(session_id)
    channel = state.get_channel(channel_name)

    try:
        user_by_name = channel.get_user(user_by_session_id.name)
    except UserNotFoundError:
        raise AccessError

    if user_by_session_id.session_id != user_by_name.session_id:
        raise AccessError

    message = UserMessage(
        sender_name=user_by_name.name,
        sender_color_id=user_by_name.color_id,
        content=data.content
    )

    action = AddMessageAction(
        channel_name=channel_name,
        message=message
    )

    await store.dispatch(action)

    return {}

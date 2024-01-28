import os
import redis.asyncio
import rstore
import secrets

from typing import Annotated, Optional

from fastapi import (
    Cookie,
    FastAPI,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware

from .action import AddUserAction, RemoveUserAction
from .middleware import system_message_middleware
from .model import App, Channel, UserData
from .reducer import app_reducer


class AccessError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=403)


client = redis.asyncio.from_url(os.environ["REDIS_URL"])
store = rstore.create_store(
    app_reducer,
    initial_state_factory=App.empty,
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


@app.on_event("startup")
async def handle_startup() -> None:
    await client.ping()
    await store.bind(client)


@app.on_event("shutdown")
async def handle_shutdown() -> None:
    await store.unbind()
    await client.close()


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: Annotated[Optional[str], Cookie()] = None
) -> None:
    if not session_id:
        raise AccessError

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
async def post_session(response: Response) -> dict:
    session_id = secrets.token_hex(32)

    response.set_cookie("session_id", session_id, httponly=True)

    return {}


@app.post("/channel/{channel_name}/user/{user_name}")
async def post_channel_user(
    channel_name: str,
    user_name: str,
    session_id: Annotated[Optional[str], Cookie()] = None
) -> Channel:
    if not session_id:
        raise AccessError

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
async def post_channel_message(channel_name: str, message: dict) -> dict:
    pass

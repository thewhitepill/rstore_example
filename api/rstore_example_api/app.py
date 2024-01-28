import os
import redis.asyncio
import rstore

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware import system_message_middleware
from .model import App
from .reducer import app_reducer


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


@app.on_event("startup")
async def handle_startup() -> None:
    await client.ping()
    await store.bind(client)


@app.on_event("shutdown")
async def handle_shutdown() -> None:
    await store.unbind()
    await client.close()

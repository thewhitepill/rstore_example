import asyncio

from typing import Coroutine


_tasks = set()


def run_task(coroutine: Coroutine) -> None:
    _tasks.add(asyncio.create_task(coroutine))

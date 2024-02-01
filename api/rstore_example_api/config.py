from types import SimpleNamespace

import os


config = SimpleNamespace(
    redis=SimpleNamespace(
        url=os.environ["REDIS_URL"]
    )
)

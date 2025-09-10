from fastapi import FastAPI

from .cors import add_cors_middleware
from .processTimer import ProcessTimerMiddleware
from .redis import RedisMiddleware
from .session import add_session_middleware


def add_middlewares(app: FastAPI) -> None:
    print("add_middlewares")
    add_cors_middleware(app)
    add_session_middleware(app)
    app.add_middleware(RedisMiddleware)
    app.add_middleware(ProcessTimerMiddleware)

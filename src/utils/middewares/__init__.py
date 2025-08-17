from fastapi import FastAPI

from .cors import add_cors_middleware
from .session import add_session_middleware


def add_middlewares(app: FastAPI) -> None:
    print("add_middlewares")
    add_cors_middleware(app)
    add_session_middleware(app)

import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware


def add_session_middleware(app: FastAPI) -> None:
    SECRET_KEY = os.getenv("SECRET_KEY")
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=3600)

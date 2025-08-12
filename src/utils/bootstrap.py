import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.utils.db.db import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting up...")

    static_dir = "src/static"
    # 'src/static' 디렉토리가 없는 경우 생성
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir)

    app.mount("/src/static", StaticFiles(directory=static_dir), name="static")

    yield
    print("Shutting down...")
    db.engine.dispose()

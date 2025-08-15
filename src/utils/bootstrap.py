import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.router import blog, user
from src.utils import error_handler
from src.utils.db.db import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting up...")

    static_dir = "src/static"
    # 'src/static' 디렉토리가 없는 경우 생성
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir)

    app.mount("/src/static", StaticFiles(directory=static_dir), name="static")

    app.include_router(blog.router)
    app.include_router(user.router)

    app.add_exception_handler(
        HTTPException, error_handler.custom_http_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError, error_handler.custom_validation_exception_handler
    )
    app.add_exception_handler(
        StarletteHTTPException, error_handler.custom_starlette_http_exception_handler
    )

    yield
    print("Shutting down...")
    await db.engine.dispose()

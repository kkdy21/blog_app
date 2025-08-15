from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.router import blog, user
from src.utils import error_handler
from src.utils.bootstrap import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(blog.router)
app.include_router(user.router)

app.add_exception_handler(HTTPException, error_handler.custom_http_exception_handler)
app.add_exception_handler(
    RequestValidationError, error_handler.custom_validation_exception_handler
)
app.add_exception_handler(
    StarletteHTTPException, error_handler.custom_starlette_http_exception_handler
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    from time import perf_counter

    start = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    return response

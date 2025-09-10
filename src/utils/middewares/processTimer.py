from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ProcessTimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = perf_counter()
        response = await call_next(request)
        duration_ms = (perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        return response

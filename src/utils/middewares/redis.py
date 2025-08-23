import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.manager.session_redis_manager import SessionRedisManager


class RedisMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        session_cookie_key: str = "session_id",
        max_age: int = 60 * 60,
    ):
        super().__init__(app)
        self.session_cookie_key = session_cookie_key
        self.max_age = max_age
        self.session_manager = SessionRedisManager()

    # dispatch 메서드를 오버라이드 해서 쓰면된다는 근거 찾기
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        session_id = request.cookies.get(self.session_cookie_key)
        if session_id:
            session_data = await self.session_manager._get_redis_session(session_id)

            request.state.session = session_data if session_data else {}
        else:
            request.state.session = {}
        initial_session_data = dict(request.state.session)

        response = await call_next(request)

        final_session_data = request.state.session

        if initial_session_data and not final_session_data:
            if session_id:
                await self.session_manager._delete_redis_session(session_id)
            response.delete_cookie(self.session_cookie_key)

        if final_session_data and initial_session_data != final_session_data:
            current_session_id = session_id or str(uuid.uuid4())
            await self.session_manager._set_redis_session(
                current_session_id, final_session_data
            )
            response.set_cookie(
                key=self.session_cookie_key,
                value=current_session_id,
                max_age=self.max_age,
                httponly=True,
                samesite="lax",
            )

        return response

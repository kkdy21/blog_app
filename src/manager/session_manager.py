from dataclasses import dataclass
from typing import Any

from fastapi import Request

from src.model.user.database import UserData


@dataclass
class SessionUser:
    id: int
    name: str
    email: str


class SessionManager:
    def __init__(self, request: Request):
        self.request = request

    def _set_session(self, key: str, value: Any) -> None:
        self.request.session[key] = value

    def _get_session(self, key: str) -> Any:
        return self.request.session.get(key)

    def set_session_user(self, user: UserData) -> None:
        session_user = SessionUser(
            id=user.id,
            name=user.name,
            email=user.email,
        )
        self._set_session("session_user", session_user)

    def get_is_authorized(
        self, session_user: SessionUser | None, blog_author_id: int, blog_email: str
    ) -> bool:
        if session_user is None:
            return False
        if (session_user.id == blog_author_id) and (session_user.email == blog_email):
            return True
        return False

    def get_session_user(self) -> Any:
        # session을 저장할때 객체가 직렬화/역직렬화 과정을 거치면서 원본 클래스 정보를 잃어버림. 추후 redis로 변경할예정이므로 그냥 넘어감.
        return self._get_session("session_user")

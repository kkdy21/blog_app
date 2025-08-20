from dataclasses import asdict, dataclass
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
        # 객체 대신 asdict를 사용해 딕셔너리를 세션에 저장
        self._set_session("session_user", asdict(session_user))

    def get_is_authorized(
        self,
        session_user: SessionUser | None,
        blog_author_id: int,
    ) -> bool:
        if session_user is None:
            return False
        if session_user.id == blog_author_id:
            return True
        return False

    def get_session_user(self) -> SessionUser | None:
        # 세션에서 딕셔너리를 가져옴
        session_data = self._get_session("session_user")
        if session_data and isinstance(session_data, dict):
            try:
                # 딕셔너리를 다시 SessionUser 객체로 복원
                return SessionUser(**session_data)
            except TypeError:
                # 세션 데이터의 구조가 변경되었거나 손상된 경우,
                # 안전하게 None을 반환하여 로그아웃된 것으로 처리합니다.
                self.request.session.pop("session_user", None)
                return None
        return None

from dataclasses import dataclass

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

    def set_session_user(self, user: UserData) -> None:
        self.request.session["session_user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }

    def set_is_authorized(
        self, session_user: SessionUser | None, blog_author_id: int, blog_email: str
    ) -> bool:
        if session_user is None:
            return False
        if (session_user.id == blog_author_id) and (session_user.email == blog_email):
            return True
        return False

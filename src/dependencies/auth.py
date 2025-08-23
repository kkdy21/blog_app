from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from src.model.user.database import UserData


# 로그인 여부와 상관없이 호출
def get_current_user_or_none(request: Request) -> UserData | None:
    session_data = request.state.session
    if session_data:
        try:
            return UserData(**session_data)
        except Exception:
            return None
    return None


# 로그인이 필요한 API를 위한 의존성 주입
def get_current_user(
    user: UserData | None = Depends(get_current_user_or_none),
) -> UserData:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return user

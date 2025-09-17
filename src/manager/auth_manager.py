from fastapi import Request

from src.model.user.database import UserDataPass


def login(request: Request, user: UserDataPass) -> None:
    """
    사용자를 로그인 처리합니다.

    request.state.session에 사용자 정보를 할당하여,
    미들웨어가 이 변경을 감지하고 세션을 생성/갱신하도록 합니다.
    """
    request.state.session = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_email_verified": user.is_email_verified,
    }


def logout(request: Request) -> None:
    """
    사용자를 로그아웃 처리합니다.

    request.state.session을 비워,
    미들웨어가 이 변경을 감지하고 세션을 삭제하도록 합니다.
    """
    request.state.session.clear()

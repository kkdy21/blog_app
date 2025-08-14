from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.utils.jinja_template import jinja_manager


async def custom_http_exception_handler(
    request: Request, exc: HTTPException
) -> HTMLResponse:
    return jinja_manager.templates.TemplateResponse(
        request=request,
        name="http_error.html",
        context={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "title_message": "에러 발생",
        },
        status_code=exc.status_code,
    )


async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> HTMLResponse:
    # 오류 메시지를 사용자 친화적으로 가공합니다.
    error_messages = []
    for error in exc.errors():
        # loc 튜플의 마지막 요소를 필드 이름으로 사용합니다. 예: ('body', 'title') -> 'title'
        field = error["loc"][-1]
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    return jinja_manager.templates.TemplateResponse(
        request=request,
        name="http_error.html",
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": error_messages,
            "title_message": "입력 값에 문제가 있습니다.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def custom_starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> HTMLResponse:
    status_code = exc.status_code
    title = "에러 발생"
    detail: str | list[str] = (
        exc.detail if exc.detail else "요청 처리 중 오류가 발생했습니다."
    )

    if status_code == status.HTTP_404_NOT_FOUND:
        title = "페이지를 찾을 수 없습니다."
        if not exc.detail:
            detail = "요청하신 주소가 올바르지 않습니다."

    return jinja_manager.templates.TemplateResponse(
        request=request,
        name="http_error.html",
        context={
            "status_code": status_code,
            "detail": detail,
            "title_message": title,
        },
        status_code=status_code,
    )

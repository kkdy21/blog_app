from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

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

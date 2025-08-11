from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from src.router import blog
from src.utils import error_handler
from src.utils.bootstrap import lifespan

app = FastAPI(lifespan=lifespan)

# 정적 파일 서빙을 위한 마운트 설정
# app.mount(): FastAPI 애플리케이션에 다른 ASGI 애플리케이션을 마운트하는 함수
# - "/static": URL 경로 (브라우저에서 /static/...로 접근)
# - StaticFiles(directory="static"): static 디렉토리의 파일들을 서빙하는 ASGI 앱
# - name="static": 마운트 이름 (URL 역참조 등에 사용)
# 예시: static/images/blog_default.png → http://localhost:8000/static/images/blog_default.png
app.mount("/src/static", StaticFiles(directory="src/static"), name="static")

app.include_router(blog.router)

app.add_exception_handler(HTTPException, error_handler.custom_http_exception_handler)
app.add_exception_handler(
    RequestValidationError, error_handler.custom_validation_exception_handler
)

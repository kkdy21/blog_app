from fastapi import APIRouter, Depends, Form, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.manager.auth_manager import logout
from src.service.user_svc import UserService
from src.utils.db.db import get_db_session
from src.utils.jinja_template import jinja_manager

router = APIRouter(prefix="/users", tags=["users"])

template = jinja_manager.templates


@router.get("/sign_in")
async def get_sign_in_ui(request: Request) -> HTMLResponse:
    return template.TemplateResponse(
        request=request,
        name="sign_in.html",
    )


@router.post("/sign_in")
async def sign_in(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    await UserService().sign_in(request, email, password, session)
    return RedirectResponse(url="/blogs", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/sign_up")
async def get_sign_up_ui(request: Request) -> HTMLResponse:
    return template.TemplateResponse(
        request=request,
        name="sign_up.html",
    )


@router.post("/sign_up")
async def sign_up(
    request: Request,
    name: str = Form(min_length=2, max_length=100),
    email: EmailStr = Form(),
    password: str = Form(min_length=8, max_length=100),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    await UserService().create_user(name, email, password, session)
    return RedirectResponse(url="/users/sign_in", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/sign_out")
async def sign_out(request: Request) -> RedirectResponse:
    logout(request)
    return RedirectResponse(url="/users/sign_in", status_code=status.HTTP_303_SEE_OTHER)

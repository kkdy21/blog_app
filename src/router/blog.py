from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user, get_current_user_or_none
from src.model.user.orm import User
from src.model.user.response import UserResponse
from src.service.blog_svc import BlogService
from src.service.comment_svc import CommentService
from src.utils.db.db import get_db_session
from src.utils.jinja_template import jinja_manager

router = APIRouter(prefix="/blogs", tags=["blogs"])

template = jinja_manager.templates


# 모든 블로그 글 조회
@router.get("/")
async def get_all_blogs(
    request: Request,
    current_user: User | None = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_db_session),
) -> HTMLResponse:
    all_blogs_dto = await BlogService().get_all_blogs(session)
    return template.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "all_blogs": all_blogs_dto,
            "session_user": current_user,
        },
        status_code=200,
    )


# 특정 블로그 조회
@router.get("/show/{blog_id}")
async def get_blog_by_id(
    request: Request,
    blog_id: int,
    current_user: User | None = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_db_session),
) -> HTMLResponse:
    blog_dto = await BlogService().get_blog_by_id(blog_id, session)
    comments = await CommentService().get_comments_by_blog_id(blog_id, session)

    session_user_dto = (
        UserResponse.model_validate(current_user) if current_user else None
    )

    return template.TemplateResponse(
        request=request,
        name="show_blog.html",
        context={
            "request": request,
            "blog": blog_dto,
            "comments": comments,
            "session_user": session_user_dto,
            "is_valid_auth": current_user and current_user.id == blog_dto.author.id,
        },
        status_code=200,
    )


# 블로그 생성
@router.get("/new")
def get_create_blog_ui(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    return template.TemplateResponse(
        request=request,
        name="new_blog.html",
        context={"session_user": current_user},
    )


@router.post("/new")
async def create_blog(
    current_user: User = Depends(get_current_user),
    title: str = Form(min_length=2, max_length=200),
    content: str = Form(min_length=2, max_length=4000),
    tags: str = Form(""),
    image_file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    await BlogService().create_blog(
        title, content, tags, image_file, session, current_user
    )
    return RedirectResponse(url="/blogs", status_code=status.HTTP_303_SEE_OTHER)


# 특정 블로그 update
@router.get("/modify/{blog_id}")
async def get_update_blog_ui(
    request: Request,
    blog_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    blog_orm = await BlogService()._get_blog_orm_by_id(blog_id, session)

    return template.TemplateResponse(
        request=request,
        name="modify_blog.html",
        context={"blog": blog_orm, "session_user": current_user},
    )


@router.post("/modify/{blog_id}")
async def update_blog(
    blog_id: int,
    title: str = Form(min_length=2, max_length=200),
    content: str = Form(min_length=2, max_length=4000),
    tags: str = Form(""),
    image_file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    await BlogService().update_blog(
        blog_id, title, content, tags, image_file, session, current_user
    )
    return RedirectResponse(
        url=f"/blogs/show/{blog_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.delete("/delete/{blog_id}")
async def delete_blog(
    blog_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    await BlogService().delete_blog(blog_id, session, current_user)
    return JSONResponse(
        content={"message": "Blog deleted successfully"}, status_code=status.HTTP_200_OK
    )


@router.get("/tags/{tag_name}")
async def get_blogs_by_tag(
    request: Request,
    tag_name: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_current_user_or_none),
) -> HTMLResponse:
    blogs_dto = await BlogService().get_blogs_by_tag(tag_name, session)
    return template.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "all_blogs": blogs_dto,
            "session_user": current_user,
            "filter_tag": tag_name,
        },
        status_code=200,
    )

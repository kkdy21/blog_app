from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from src.dependencies.auth import get_current_user, get_current_user_or_none
from src.model.blog.database import BlogData
from src.model.user.database import UserData
from src.service.blog_svc import BlogService
from src.utils.db.db import get_connection_db
from src.utils.jinja_template import jinja_manager

router = APIRouter(prefix="/blogs", tags=["blogs"])

template = jinja_manager.templates


# 모든 블로그 글 조회
@router.get("/")
async def get_all_blogs(
    request: Request,
    current_user: UserData | None = Depends(get_current_user_or_none),
    conn: AsyncConnection = Depends(get_connection_db),
) -> HTMLResponse:
    all_blogs_dto = await BlogService().get_all_blogs(conn)
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
    current_user: UserData | None = Depends(get_current_user_or_none),
    conn: AsyncConnection = Depends(get_connection_db),
) -> HTMLResponse:
    blog_dto = await BlogService().get_blog_by_id(blog_id, conn)

    return template.TemplateResponse(
        request=request,
        name="show_blog.html",
        context={
            "request": request,
            "blog": blog_dto,
            "session_user": current_user,
        },
        status_code=200,
    )


# 블로그 생성
@router.get("/new")
def get_create_blog_ui(
    request: Request,
    current_user: UserData = Depends(get_current_user),
) -> HTMLResponse:
    return template.TemplateResponse(
        request=request,
        name="new_blog.html",
        context={"session_user": current_user},
    )


@router.post("/new")
async def create_blog(
    current_user: UserData = Depends(get_current_user),
    title: str = Form(min_length=2, max_length=200),
    content: str = Form(min_length=2, max_length=4000),
    image_file: UploadFile = File(None),
    conn: AsyncConnection = Depends(get_connection_db),
) -> RedirectResponse:
    await BlogService().create_blog(title, content, image_file, conn, current_user)
    return RedirectResponse(url="/blogs", status_code=status.HTTP_303_SEE_OTHER)


# 특정 블로그 update
@router.get("/modify/{blog_id}")
async def get_update_blog_ui(
    request: Request,
    blog_id: int,
    conn: AsyncConnection = Depends(get_connection_db),
    current_user: UserData = Depends(get_current_user),
) -> HTMLResponse:
    blog_dto: BlogData = await BlogService().get_blog_by_id(blog_id, conn)

    return template.TemplateResponse(
        request=request,
        name="modify_blog.html",
        context={"blog": blog_dto, "session_user": current_user},
    )


@router.post("/modify/{blog_id}")
async def update_blog(
    blog_id: int,
    title: str = Form(min_length=2, max_length=200),
    author_id: int = Form(max_length=100),
    content: str = Form(min_length=2, max_length=4000),
    image_file: UploadFile = File(None),
    conn: AsyncConnection = Depends(get_connection_db),
    current_user: UserData = Depends(get_current_user),
) -> RedirectResponse:
    await BlogService().update_blog(
        author_id, blog_id, title, content, image_file, conn, current_user
    )
    return RedirectResponse(
        url=f"/blogs/show/{blog_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.delete("/delete/{blog_id}")
async def delete_blog(
    blog_id: int,
    conn: AsyncConnection = Depends(get_connection_db),
    current_user: UserData = Depends(get_current_user),
) -> JSONResponse:
    await BlogService().delete_blog(blog_id, conn, current_user)
    return JSONResponse(
        content={"message": "Blog deleted successfully"}, status_code=status.HTTP_200_OK
    )

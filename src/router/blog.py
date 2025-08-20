from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from src.manager.session_manager import SessionManager
from src.model.blog.database import BlogData
from src.service.blog_svc import BlogService
from src.utils.db.db import get_connection_db
from src.utils.jinja_template import jinja_manager

router = APIRouter(prefix="/blogs", tags=["blogs"])

template = jinja_manager.templates


# 모든 블로그 글 조회
@router.get("/")
async def get_all_blogs(
    request: Request,
    conn: AsyncConnection = Depends(get_connection_db),
    session_manager: SessionManager = Depends(SessionManager),
) -> HTMLResponse:
    all_blogs_dto = await BlogService().get_all_blogs(conn)
    return template.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "all_blogs": all_blogs_dto,
            "session_user": session_manager.get_session_user(),
        },
        status_code=200,
    )


# 특정 블로그 조회
@router.get("/show/{blog_id}")
async def get_blog_by_id(
    request: Request,
    blog_id: int,
    conn: AsyncConnection = Depends(get_connection_db),
    session_manager: SessionManager = Depends(SessionManager),
) -> HTMLResponse:
    blog_dto = await BlogService().get_blog_by_id(blog_id, conn)

    return template.TemplateResponse(
        request=request,
        name="show_blog.html",
        context={
            "request": request,
            "blog": blog_dto,
            "session_user": session_manager.get_session_user(),
        },
        status_code=200,
    )


# 블로그 생성
@router.get("/new")
def get_create_blog_ui(
    request: Request, session_manager: SessionManager = Depends(SessionManager)
) -> HTMLResponse:
    return template.TemplateResponse(
        request=request,
        name="new_blog.html",
        context={"session_user": session_manager.get_session_user()},
    )


@router.post("/new")
async def create_blog(
    request: Request,
    title: str = Form(min_length=2, max_length=200),
    content: str = Form(min_length=2, max_length=4000),
    image_file: UploadFile = File(None),
    conn: AsyncConnection = Depends(get_connection_db),
    session_manager: SessionManager = Depends(SessionManager),
) -> RedirectResponse:
    await BlogService().create_blog(title, content, image_file, conn, session_manager)
    return RedirectResponse(url="/blogs", status_code=status.HTTP_303_SEE_OTHER)


# 특정 블로그 update
@router.get("/modify/{blog_id}")
async def get_update_blog_ui(
    request: Request,
    blog_id: int,
    conn: AsyncConnection = Depends(get_connection_db),
    session_manager: SessionManager = Depends(SessionManager),
) -> HTMLResponse:
    blog_dto: BlogData = await BlogService().get_blog_by_id(blog_id, conn)

    return template.TemplateResponse(
        request=request,
        name="modify_blog.html",
        context={
            "blog": blog_dto,
            "session_user": session_manager.get_session_user(),
        },
    )


@router.post("/modify/{blog_id}")
async def update_blog(
    request: Request,
    blog_id: int,
    title: str = Form(min_length=2, max_length=200),
    author: str = Form(max_length=100),
    content: str = Form(min_length=2, max_length=4000),
    image_file: UploadFile = File(None),
    conn: AsyncConnection = Depends(get_connection_db),
    session_manager: SessionManager = Depends(SessionManager),
) -> RedirectResponse:
    await BlogService().update_blog(
        blog_id, title, content, image_file, conn, session_manager
    )
    return RedirectResponse(
        url=f"/blogs/show/{blog_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.delete("/delete/{blog_id}")
async def delete_blog(
    request: Request,
    blog_id: int,
    conn: AsyncConnection = Depends(get_connection_db),
    session_manager: SessionManager = Depends(SessionManager),
) -> JSONResponse:
    await BlogService().delete_blog(blog_id, conn, session_manager)
    return JSONResponse(
        content={"message": "Blog deleted successfully"}, status_code=status.HTTP_200_OK
    )

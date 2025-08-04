from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from src.model.blog.database import BlogData
from src.utils.db.db import get_connection_db

router = APIRouter(prefix="/blog", tags=["blog"])
template = Jinja2Templates(directory="src/templates")


# 모든 블로그 글 조회
@router.get("/")
async def get_all_blogs(
    request: Request, conn: Connection = Depends(get_connection_db)
) -> HTMLResponse:
    try:
        query = """
        select * from blog
        order by modified_dt desc;
        """
        result = conn.execute(text(query))
        all_blogs = result.fetchall()
        all_blogs_dto = [
            BlogData(
                id=blog.id,
                title=blog.title,
                author=blog.author,
                content=blog.content,
                modified_dt=blog.modified_dt,
                image_loc=blog.image_loc,
            )
            for blog in all_blogs
        ]

        return template.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "all_blogs": all_blogs_dto},
            status_code=200,
        )
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터베이스 연결 실패",
        ) from e

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="알수없는 에러 발생",
        ) from e


# 특정 블로그 update

# 특정 블로그 삭제

# 블로그 생성

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from src.model.blog.database import BlogData
from src.utils.text_handler import newline_to_br, truncate_text


class BlogService:
    def get_all_blogs(self, conn: Connection) -> list[BlogData]:
        try:
            query = """
                    select * from blog
                    order by modified_dt desc;
                    """
            result = conn.execute(text(query))
            all_blog_vos = result.fetchall()
            all_blog_dto = [
                BlogData(
                    id=blog.id,
                    title=blog.title,
                    author=blog.author,
                    content=truncate_text(newline_to_br(blog.content)),
                    modified_dt=blog.modified_dt,
                    image_loc=blog.image_loc,
                )
                for blog in all_blog_vos
            ]

            return all_blog_dto

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알수없는 에러 발생: {str(e)}",
            ) from e

    def get_blog_by_id(self, blog_id: int, conn: Connection) -> BlogData:
        try:
            query = """
                    select * from blog
                    where id = :blog_id;
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(blog_id=blog_id)

            result = conn.execute(bind_stmt)
            blog_vo = result.fetchone()
            if not blog_vo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )

            blog_dto = BlogData(
                id=blog_vo.id,
                title=blog_vo.title,
                author=blog_vo.author,
                content=newline_to_br(blog_vo.content),
                modified_dt=blog_vo.modified_dt,
                image_loc=blog_vo.image_loc,
            )
            return blog_dto
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알수없는 에러 발생: {str(e)}",
            ) from e

    def create_blog(
        self, title: str, author: str, content: str, conn: Connection
    ) -> None:
        try:
            query = """
                    insert into blog (title, author, content, modified_dt)
                    values (:title, :author, :content, now());
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(
                title=title,
                author=author,
                content=content,
            )
            conn.execute(bind_stmt)

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="블로그 생성 실패",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알수없는 에러 발생: {str(e)}",
            ) from e

    def delete_blog(self, blog_id: int, conn: Connection) -> None:
        try:
            query = """
                    delete from blog
                    where id = :blog_id;
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(blog_id=blog_id)
            conn.execute(bind_stmt)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알수없는 에러 발생: {str(e)}",
            ) from e

    def update_blog(
        self,
        blog_id: int,
        title: str,
        author: str,
        content: str,
        conn: Connection,
    ) -> None:
        try:
            query = """
                    update blog
                    set title = :title, author = :author, content = :content, modified_dt = now()
                    where id = :blog_id;
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(
                blog_id=blog_id,
                title=title,
                author=author,
                content=content,
            )
            result = conn.execute(bind_stmt)

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알수없는 에러 발생: {str(e)}",
            ) from e

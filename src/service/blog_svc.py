from fastapi import HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

from src.manager.image_manager import ImageManager
from src.manager.session_manager import SessionManager
from src.model.blog.database import BlogData
from src.utils.text_helper import newline_to_br, truncate_text


class BlogService:
    def __init__(self) -> None:
        self.image_manager = ImageManager()

    async def get_all_blogs(self, conn: AsyncConnection) -> list[BlogData]:
        try:
            query = """
                    select * from blog as b
                    order by modified_dt desc
                    join user as u on b.author_id = u.id;
                    """
            result = await conn.execute(text(query))
            all_blog_vos = result.fetchall()
            all_blog_dto = [
                BlogData(
                    id=blog.id,
                    title=blog.title,
                    author_id=blog.author_id,
                    content=truncate_text(newline_to_br(blog.content)),
                    modified_dt=blog.modified_dt,
                    image_loc=self.image_manager.resolve_image_url(blog.image_loc),
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

    async def get_blog_by_id(self, blog_id: int, conn: AsyncConnection) -> BlogData:
        try:
            query = """
                    select * from blog
                    where id = :blog_id;
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(blog_id=blog_id)

            result = await conn.execute(bind_stmt)
            blog_vo = result.fetchone()
            if not blog_vo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )

            blog_dto = BlogData(
                id=blog_vo.id,
                title=blog_vo.title,
                author_id=blog_vo.author_id,
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

    async def create_blog(
        self,
        title: str,
        content: str,
        image_file: UploadFile | None,
        conn: AsyncConnection,
        session_manager: SessionManager,
    ) -> None:
        try:
            session_user = session_manager.get_session_user()
            if session_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="로그인이 필요합니다.",
                )

            image_loc = None
            if image_file:
                image_loc = await self.image_manager.save_image(
                    session_user.name, image_file
                )

            query = """
                    insert into blog (title, author_id, content, modified_dt, image_loc)
                    values (:title, :author_id, :content, now(), :image_loc);
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(
                title=title,
                author_id=session_user.id,
                content=content,
                image_loc=image_loc,
            )
            await conn.execute(bind_stmt)

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

    async def delete_blog(self, blog_id: int, conn: AsyncConnection) -> None:
        try:
            query = """
                    delete from blog
                    where id = :blog_id;
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(blog_id=blog_id)
            await conn.execute(bind_stmt)
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

    async def update_blog(
        self,
        blog_id: int,
        title: str,
        content: str,
        image_file: UploadFile | None,
        conn: AsyncConnection,
        session_manager: SessionManager,
    ) -> None:
        try:
            session_user = session_manager.get_session_user()
            if session_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="로그인이 필요합니다.",
                )

            image_loc = None
            if image_file:
                image_loc = self.image_manager.save_image(session_user.id, image_file)

            query = """
                    update blog
                    set title = :title, author_id = :author_id, content = :content, modified_dt = now(), image_loc = :image_loc
                    where id = :blog_id;
                    """
            stmt = text(query)
            bind_stmt = stmt.bindparams(
                blog_id=blog_id,
                title=title,
                author_id=session_user.id,
                content=content,
                image_loc=image_loc,
            )
            result = await conn.execute(bind_stmt)

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"알수없는 에러 발생: {str(e)}",
            ) from e

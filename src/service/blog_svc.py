from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.manager.image_manager import ImageManager
from src.model.blog.orm import Blog
from src.model.blog.response import BlogListResponse, BlogResponse
from src.model.user.orm import User
from src.utils.text_helper import newline_to_br


class BlogService:
    def __init__(self) -> None:
        self.image_manager = ImageManager()

    async def _get_blog_orm_by_id(
        self, blog_id: int, session: AsyncSession
    ) -> Blog | None:
        """
        내부 로직 전용: ID로 원본 Blog ORM 객체를 가져옵니다.
        """
        stmt = select(Blog).options(joinedload(Blog.author)).where(Blog.id == blog_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_blogs(self, session: AsyncSession) -> list[BlogListResponse]:
        """
        블로그 목록 페이지를 위한 DTO 리스트를 반환합니다.
        """
        try:
            stmt = (
                select(Blog)
                .options(joinedload(Blog.author))
                .order_by(Blog.modified_dt.desc())
            )
            result = await session.execute(stmt)
            blogs_orm = result.scalars().all()

            # ORM 객체 리스트를 Pydantic DTO 리스트로 변환
            # BlogListResponse가 자동으로 내용을 자릅니다.
            blog_dtos = [BlogListResponse.model_validate(b) for b in blogs_orm]

            for blog_dto in blog_dtos:
                blog_dto.image_loc = self.image_manager.resolve_image_url(
                    blog_dto.image_loc
                )
            return blog_dtos

        except Exception as e:
            # 디버깅 로그는 유지
            print(f"Error in get_all_blogs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"블로그 목록을 가져오는 중 오류 발생: {e}",
            ) from e

    async def get_blog_by_id(self, blog_id: int, session: AsyncSession) -> BlogResponse:
        """
        블로그 상세 페이지를 위한 DTO를 반환합니다.
        """
        try:
            blog_orm = await self._get_blog_orm_by_id(blog_id, session)

            if not blog_orm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )

            # ORM 객체를 BlogResponse DTO로 변환
            blog_dto = BlogResponse.model_validate(blog_orm)

            # DTO의 content를 가공 (줄바꿈 처리)
            blog_dto.content = newline_to_br(blog_dto.content)
            blog_dto.image_loc = self.image_manager.resolve_image_url(
                blog_dto.image_loc
            )

            return blog_dto
        except Exception as e:
            print(f"Error in get_blog_by_id: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"블로그를 가져오는 중 오류 발생: {e}",
            ) from e

    async def create_blog(
        self,
        title: str,
        content: str,
        image_file: UploadFile | None,
        session: AsyncSession,
        session_user: User,
    ) -> None:
        try:
            if not session_user.id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="로그인이 필요합니다.",
                )

            image_loc = None
            if image_file and image_file.filename:
                image_loc = await self.image_manager.save_image(
                    session_user.email, image_file
                )

            new_blog = Blog(
                title=title,
                content=content,
                author_id=session_user.id,
                image_loc=image_loc,
            )
            session.add(new_blog)
            await session.flush()

        except SQLAlchemyError as e:
            print(f"SQLAlchemyError in create_blog: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="블로그 생성 실패",
            ) from e

    async def delete_blog(
        self, blog_id: int, session: AsyncSession, session_user: User
    ) -> None:
        try:
            blog_orm = await self._get_blog_orm_by_id(blog_id, session)
            if not blog_orm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )

            if not self._is_authorized(session_user, blog_orm.author_id):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="권한이 없습니다.",
                )
            stmt = delete(Blog).where(Blog.id == blog_id)
            await session.execute(stmt)

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e

    async def update_blog(
        self,
        blog_id: int,
        title: str,
        content: str,
        image_file: UploadFile | None,
        session: AsyncSession,
        session_user: User,
    ) -> None:
        try:
            blog_orm = await self._get_blog_orm_by_id(blog_id, session)
            if not blog_orm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="블로그 글을 찾을 수 없습니다.",
                )

            if not self._is_authorized(session_user, blog_orm.author_id):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="권한이 없습니다.",
                )

            image_loc = blog_orm.image_loc
            if image_file and image_file.filename:
                image_loc = await self.image_manager.save_image(
                    session_user.email, image_file
                )

            stmt = (
                update(Blog)
                .where(Blog.id == blog_id)
                .values(
                    title=title,
                    content=content,
                    image_loc=image_loc,
                )
            )
            result = await session.execute(stmt)

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

    def _is_authorized(self, session_user: User, author_id: int) -> bool:
        return session_user.id == author_id

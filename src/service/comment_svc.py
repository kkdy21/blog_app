from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.model.comment.orm import Comment
from src.model.comment.request import CommentRequest
from src.model.user.orm import User


class CommentService:
    def __init__(self) -> None:
        pass

    async def create_comment(
        self, comment: CommentRequest, session: AsyncSession, session_user: User
    ) -> None:
        try:
            if not session_user.id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="로그인이 필요합니다.",
                )

            new_comment = Comment(
                content=comment.content,
                blog_id=comment.blog_id,
                parent_id=comment.parent_id,
                author_id=session_user.id,
            )
            session.add(new_comment)
            await session.flush()

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="댓글 생성 실패",
            ) from e

    async def get_comment(self, comment_id: int) -> Comment:
        pass

    async def update_comment(self, comment_id: int, comment: Comment) -> None:
        pass

    async def delete_comment(self, comment_id: int) -> None:
        pass

    async def get_comments_by_blog_id(
        self, blog_id: int, session: AsyncSession
    ) -> list[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.blog_id == blog_id)
            # parent_id가 NULL인 댓글(최상위 댓글)만 먼저 선택합니다.
            .where(Comment.parent_id == None)
            .options(
                # 각 최상위 댓글의 'replies'(대댓글)를 미리 로드합니다.
                # 이 때, 대댓글의 작성자 정보도 함께 로드합니다.
                selectinload(Comment.replies).options(joinedload(Comment.author)),
                # 최상위 댓글의 작성자 정보도 로드합니다.
                joinedload(Comment.author),
            )
            .order_by(Comment.created_at.asc())
        )

        result = await session.execute(stmt)
        return result.scalars().all()

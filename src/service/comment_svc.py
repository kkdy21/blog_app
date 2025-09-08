from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.model.comment.orm import Comment
from src.model.comment.request import CommentRequest
from src.model.user.orm import User


class CommentService:
    @staticmethod
    def _serialize_comment(
        comment: Comment, children_map: dict[int, list[Comment]]
    ) -> dict:
        """재귀적으로 Comment 객체를 JSON 직렬화"""
        return {
            "id": comment.id,
            "content": comment.content,
            "author": {"id": comment.author.id, "name": comment.author.name}
            if comment.author
            else None,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at.isoformat()
            if comment.created_at
            else None,
            "replies": [
                CommentService._serialize_comment(reply, children_map)
                for reply in sorted(
                    children_map.get(comment.id, []),
                    key=lambda r: r.created_at
                    if isinstance(r.created_at, datetime)
                    else datetime.fromisoformat(r.created_at),
                )
            ],
        }

    async def create_comment(
        self, comment: CommentRequest, session: AsyncSession, session_user: User
    ) -> Comment:
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
            await session.refresh(new_comment, ["author"])

            # 새 댓글은 children_map이 필요 없으므로 replies = [] 처리
            return new_comment

        except SQLAlchemyError as e:
            print(f"SQLAlchemyError in create_comment: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="댓글 생성 실패",
            ) from e

    async def get_comment_by_comment_id(
        self, comment_id: int, session: AsyncSession
    ) -> Comment:
        try:
            stmt = (
                select(Comment)
                .where(Comment.id == comment_id)
                .options(joinedload(Comment.author))
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e

    async def update_comment(
        self,
        comment_id: int,
        comment: CommentRequest,
        session: AsyncSession,
        session_user: User,
    ) -> dict:
        try:
            comment_orm = await self.get_comment_by_comment_id(comment_id, session)
            if not comment_orm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="댓글을 찾을 수 없습니다.",
                )

            if not self._is_authorized(session_user, comment_orm.author_id):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="권한이 없습니다.",
                )

            stmt = (
                update(Comment)
                .where(Comment.id == comment_id)
                .values(content=comment.content)
            )
            await session.execute(stmt)
            await session.flush()
            await session.refresh(comment_orm, ["author"])

            return {
                "id": comment_orm.id,
                "content": comment_orm.content,
                "author": {
                    "id": comment_orm.author.id,
                    "name": comment_orm.author.name,
                },
                "parent_id": comment_orm.parent_id,
                "created_at": comment_orm.created_at.isoformat()
                if comment_orm.created_at
                else None,
                "replies": [],  # 수정 시에는 replies 불필요
            }

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e

    async def delete_comment(
        self, comment_id: int, session: AsyncSession, session_user: User
    ) -> None:
        try:
            comment_orm = await self.get_comment_by_comment_id(comment_id, session)
            if not comment_orm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="댓글을 찾을 수 없습니다.",
                )

            if not self._is_authorized(session_user, comment_orm.author_id):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="권한이 없습니다.",
                )

            stmt = delete(Comment).where(Comment.id == comment_id)
            await session.execute(stmt)

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e

    async def get_comments_by_blog_id(
        self, blog_id: int, session: AsyncSession
    ) -> list[dict]:
        try:
            # 최상위 댓글 가져오기
            stmt_top = (
                select(Comment)
                .where(Comment.blog_id == blog_id)
                .where(Comment.parent_id == None)
                .options(joinedload(Comment.author))
                .order_by(Comment.created_at.asc())
            )
            result_top = await session.execute(stmt_top)
            top_comments = result_top.scalars().unique().all()

            # 모든 댓글을 한 번에 가져오기
            stmt_all = (
                select(Comment)
                .where(Comment.blog_id == blog_id)
                .options(joinedload(Comment.author))
                .order_by(Comment.created_at.asc())
            )
            result_all = await session.execute(stmt_all)
            all_comments = result_all.scalars().all()

            # parent_id → children 매핑
            children_map: dict[int, list[Comment]] = {}
            for c in all_comments:
                if c.parent_id:
                    children_map.setdefault(c.parent_id, []).append(c)

            # 직렬화
            return [self._serialize_comment(c, children_map) for c in top_comments]

        except SQLAlchemyError as e:
            print(f"SQLAlchemyError in get_comments_by_blog_id: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="데이터베이스 연결 실패",
            ) from e

    def _is_authorized(self, session_user: User, author_id: int) -> bool:
        return session_user.id == author_id

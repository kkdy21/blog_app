from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.model.comment.request import CommentRequest
from src.model.user.orm import User
from src.service.comment_svc import CommentService
from src.utils.db.db import get_db_session

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/")
async def get_comments(blog_id: int, session: AsyncSession = Depends(get_db_session)):
    return await CommentService().get_comments_by_blog_id(blog_id, session)


@router.post("/")
async def create_comment(
    comment: CommentRequest,
    session: AsyncSession = Depends(get_db_session),
    session_user: User = Depends(get_current_user),
):
    return await CommentService().create_comment(comment, session, session_user)

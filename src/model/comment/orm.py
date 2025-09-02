from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import Base

if TYPE_CHECKING:
    from src.model.blog.orm import Blog
    from src.model.comment.orm import Comment
    from src.model.user.orm import User


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # 외래 키 정의
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog.id"))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    # 자기참조에 활용
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("comment.id"), nullable=True
    )

    # 관계 설정
    blog: Mapped[Blog] = relationship("Blog", back_populates="comments")
    author: Mapped[User] = relationship("User", back_populates="comments")

    # 부모 댓글과의 관계 (Many-to-One)
    # remote_side=[id]는 SQLAlchemy에게 자기 참조 관계임을 알려주는 중요한 설정입니다.
    parent: Mapped[Comment | None] = relationship(
        "Comment", back_populates="replies", remote_side=[id]
    )

    # 자식 댓글(대댓글) 목록과의 관계(One-to-Many)
    replies: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="parent", cascade="all, delete-orphan"
    )

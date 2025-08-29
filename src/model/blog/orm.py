# from __future__ import annotations는 타입 힌트에서 아직 정의되지 않은 클래스 이름을 문자열처럼 사용할 수 있게 해줍니다.
# 예를 들어, Blog 클래스에서 User 타입을 힌트로 사용할 때 순환 참조(circular import) 오류를 방지합니다.
from __future__ import annotations

import datetime

# typing.TYPE_CHECKING은 타입 검사기가 코드를 분석할 때만 True가 되는 특별한 상수입니다.
# 런타임 시에는 False이므로, 실제 프로그램 실행에 영향을 주지 않으면서 타입 힌트를 위한 모듈을 가져올 수 있습니다.
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.model.base import Base

# 타입 검사 시에만 User 모델을 가져옵니다.
if TYPE_CHECKING:
    from src.model.comment.orm import Comment
    from src.model.user.orm import User


# blogs 테이블과 매핑되는 Blog ORM 모델 클래스입니다.
class Blog(Base):
    # __tablename__은 SQLAlchemy에게 이 클래스가 어떤 테이블과 매핑되는지 알려줍니다.
    __tablename__ = "blog"

    # 각 클래스 속성은 테이블의 컬럼에 해당합니다.
    # Mapped[] 타입 힌트는 이 속성이 데이터베이스 컬럼과 매핑됨을 나타냅니다.
    # mapped_column() 함수는 컬럼의 상세 속성(타입, 제약 조건 등)을 설정합니다.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    image_loc: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ForeignKey("user.id")는 이 컬럼이 'user' 테이블의 'id' 컬럼을 참조하는 외래 키임을 나타냅니다.
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    modified_dt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # 레코드가 업데이트될 때마다 현재 시간으로 갱신됩니다.
    )

    # relationship()은 다른 ORM 모델과의 관계를 정의합니다.
    # 'author' 속성을 통해 Blog 객체에서 관련된 User 객체에 접근할 수 있습니다.
    # "User"는 관계를 맺을 대상 클래스 이름입니다.
    # back_populates="blog"는 User 모델의 'blog' 속성과 양방향 관계를 설정하여 한쪽이 수정되면 반대쪽에서도 자동으로 업데이트된 결과를 반영할수있다.
    # User 객체에서도 해당 Blog 객체 목록에 접근할 수 있게 합니다.
    author: Mapped[User] = relationship("User", back_populates="blogs")
    comment: Mapped[Comment] = relationship("Comment", back_populates="blog")

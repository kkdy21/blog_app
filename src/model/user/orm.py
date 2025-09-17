# from __future__ import annotations는 타입 힌트에서 아직 정의되지 않은 클래스 이름을 문자열처럼 사용할 수 있게 해줍니다.
# 예를 들어, User 클래스에서 Blog 타입을 힌트로 사용할 때 순환 참조(circular import) 오류를 방지합니다.
from __future__ import annotations

import datetime

# typing.TYPE_CHECKING은 타입 검사기가 코드를 분석할 때만 True가 되는 특별한 상수입니다.
# 런타임 시에는 False이므로, 실제 프로그램 실행에 영향을 주지 않으면서 타입 힌트를 위한 모듈을 가져올 수 있습니다.
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.model.base import Base

# 타입 검사 시에만 Blog 모델을 가져옵니다.
from src.model.blog.orm import Blog
from src.model.comment.orm import Comment


# users 테이블과 매핑되는 User ORM 모델 클래스입니다.
class User(Base):
    # __tablename__은 SQLAlchemy에게 이 클래스가 어떤 테이블과 매핑되는지 알려줍니다.
    __tablename__ = "user"

    # 각 클래스 속성은 테이블의 컬럼에 해당합니다.
    # Mapped[] 타입 힌트는 이 속성이 데이터베이스 컬럼과 매핑됨을 나타냅니다.
    # mapped_column() 함수는 컬럼의 상세 속성(타입, 제약 조건 등)을 설정합니다.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 데이터베이스에서 기본값으로 현재 시간을 사용합니다.
    )
    is_email_verified: Mapped[bool] = mapped_column(default=False)

    # relationship()은 다른 ORM 모델과의 관계를 정의합니다.
    # 'blogs' 속성을 통해 User 객체에서 관련된 Blog 객체 목록에 접근할 수 있습니다.
    # "Blog"는 관계를 맺을 대상 클래스 이름입니다.
    # back_populates="author"는 Blog 모델의 'author' 속성과 양방향 관계를 설정하여,
    # Blog 객체에서도 해당 User 객체에 접근할 수 있게 합니다.
    blogs: Mapped[list[Blog]] = relationship("Blog", back_populates="author")
    comments: Mapped[list[Comment]] = relationship("Comment", back_populates="author")

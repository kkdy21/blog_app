from __future__ import annotations

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.model.base import Base
from src.model.blog.orm import Blog

# 다대다(Many-to-Many) 관계를 위한 연관 테이블(Association Table) 정의
# 이 테이블은 Blog와 Tag 모델을 연결하는 중간 다리 역할을 합니다.
post_tags_table = Table(
    "post_tags",  # 데이터베이스에 생성될 테이블의 이름
    Base.metadata,  # Base 모델에 연결된 메타데이터를 사용하여 테이블을 관리
    # 'blog.id'를 참조하는 외래 키(Foreign Key)이자, 복합 기본 키(Composite Primary Key)의 일부
    Column("blog_id", Integer, ForeignKey("blog.id"), primary_key=True),
    # 'tag.id'를 참조하는 외래 키(Foreign Key)이자, 복합 기본 키(Composite Primary Key)의 일부
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # "blogs" 관계 설정: Tag 모델이 어떤 Blog들과 연결되어 있는지 정의
    # SQLAlchemy가 이 관계를 통해 Tag에 연결된 Blog 목록을 자동으로 로드할 수 있게 됩니다.
    blogs: Mapped[list[Blog]] = relationship(
        "Blog",  # 관계를 맺을 대상 모델 이름
        secondary=post_tags_table,  # 다대다 관계를 맺기 위한 중간 테이블(연관 테이블)을 지정
        back_populates="tags",  # Blog 모델의 'tags' 속성과 상호 참조 관계를 설정
    )

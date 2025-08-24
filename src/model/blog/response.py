from datetime import datetime

from pydantic import BaseModel, field_validator

from src.model.user.response import UserResponse
from src.utils.text_helper import newline_to_br


# API 응답 및 템플릿에서 사용할 기본 Blog DTO 모델
class BlogResponse(BaseModel):
    id: int
    title: str
    content: str  # 원본 내용을 그대로 가짐
    modified_dt: datetime
    image_loc: str | None = None
    author: UserResponse

    # ORM 모델 객체를 Pydantic 모델로 변환할 수 있도록 설정
    class Config:
        from_attributes = True


# 블로그 목록에서 각 항목을 보여줄 때 사용할 DTO 모델
class BlogListResponse(BlogResponse):
    # 기존 BlogResponse를 상속받고 content 필드만 오버라이드
    @field_validator("content", mode="before")
    @classmethod
    def truncate_content(cls, v: str) -> str:
        # Pydantic 모델로 변환되는 과정에서 내용을 자르는 로직을 수행
        from src.utils.text_helper import truncate_text

        return truncate_text(newline_to_br(v))

from pydantic import BaseModel, Field


class CommentRequest(BaseModel):
    content: str = Field(..., description="댓글 내용")
    blog_id: int = Field(..., description="블로그 아이디")
    parent_id: int | None = Field(None, description="부모 댓글 아이디")

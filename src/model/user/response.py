from pydantic import BaseModel, EmailStr


# 사용자 정보를 응답으로 보낼 때 사용할 Pydantic 모델
# hashed_password 필드가 없으므로 절대 외부로 노출되지 않습니다.
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    # ORM 모델 객체를 Pydantic 모델로 변환할 수 있도록 설정합니다.
    # User ORM 객체를 받아서 UserResponse 모델로 자동으로 변환해줍니다.
    class Config:
        from_attributes = True

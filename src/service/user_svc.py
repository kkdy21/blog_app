from fastapi import Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from src.manager.auth_manager import login
from src.manager.password_manager import PasswordManager
from src.model.user.orm import User

password_manager = PasswordManager()


class UserService:
    async def create_user(
        self, name: str, email: str, password: str, session: AsyncSession
    ) -> None:
        try:
            # create_user 내부에서는 get_user_with_password_by_email을 호출하여
            # 이메일 중복 검사를 정확하게 수행합니다.
            if await self.get_user_by_email(email, session):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 등록된 이메일입니다.",
                )

            hashed_password = password_manager.hash(password)
            new_user = User(
                name=name,
                email=email,
                hashed_password=hashed_password,
            )
            session.add(new_user)
            await session.flush()

        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"사용자 등록 실패: {e}",
            ) from e

    async def sign_in(
        self, request: Request, email: str, password: str, session: AsyncSession
    ) -> User:
        # 로그인 시에는 비밀번호가 포함된 전체 사용자 정보가 필요합니다.
        user_vo = await self.get_user_with_password_by_email(email, session)
        if not user_vo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않는 이메일입니다.",
            )
        if not password_manager.verify(password, user_vo.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호가 일치하지 않습니다.",
            )
        login(request, user_vo)
        return user_vo

    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        # 이 메서드는 이제 비밀번호를 제외한 공개용 사용자 정보를 반환합니다.
        stmt = (
            select(User).options(defer(User.hashed_password)).where(User.email == email)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_with_password_by_email(
        self, email: str, session: AsyncSession
    ) -> User | None:
        # 이 메서드는 로그인, 회원가입 등 내부 로직에서만 사용됩니다.
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

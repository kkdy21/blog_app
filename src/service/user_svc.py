from datetime import timedelta

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from src.manager.auth_manager import login
from src.manager.password_manager import PasswordManager
from src.manager.verification_token_manager import EmailVerificationTokenManager
from src.model.user.orm import User
from src.worker.tasks import send_email

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

            # 이메일 인증 토큰 생성/저장 (Redis)
            token = EmailVerificationTokenManager.generate_token()
            await EmailVerificationTokenManager().save_token(
                token, new_user.id, ttl=timedelta(hours=1)
            )

            # 인증 메일 발송 (비동기)
            verify_link = f"http://localhost:8000/users/verify_email?token={token}"
            subject = "[Blog App] 이메일 인증을 완료해 주세요"
            body = f"""
            <h3>안녕하세요, {name}님!</h3>
            <p>아래 버튼을 눌러 이메일 인증을 완료해 주세요.</p>
            <p><a href='{verify_link}' style='display:inline-block;padding:10px 16px;background:#4f46e5;color:#fff;border-radius:8px;text-decoration:none'>이메일 인증하기</a></p>
            <p>또는 다음 링크를 복사해 브라우저에 붙여넣기: {verify_link}</p>
            <p>본 링크는 24시간 후 만료됩니다.</p>
            """
            send_email.delay(email, subject, body)

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

        if not user_vo.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일 인증이 완료되지 않았습니다.",
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

    async def verify_email(self, token: str, session: AsyncSession) -> bool:
        # Redis에서 token으로 user_id 조회 + 1회성 사용(pop)
        user_id = await EmailVerificationTokenManager().pop_user_id(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 토큰이거나 만료되었습니다.",
            )
        await session.execute(
            update(User).where(User.id == user_id).values(is_email_verified=True)
        )
        return True

    async def get_user_with_password_by_email(
        self, email: str, session: AsyncSession
    ) -> User | None:
        # 이 메서드는 로그인, 회원가입 등 내부 로직에서만 사용됩니다.
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

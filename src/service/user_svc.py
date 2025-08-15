from datetime import datetime

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

from src.manager.password_manager import PasswordManager
from src.model.user.database import UserData, UserDataPass

password_manager = PasswordManager()


class UserService:
    async def create_user(
        self, name: str, email: str, password: str, conn: AsyncConnection
    ) -> None:
        query = """
                    insert into user (name, email, hashed_password, created_at)
                    values (:name, :email, :hashed_password, :created_at)
                """
        try:
            if await self.get_user_by_email(email, conn):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 등록된 이메일입니다.",
                )

            hashed_password = password_manager.hash(password)

            stmt = text(query)
            bind_params = stmt.bindparams(
                name=name,
                email=email,
                hashed_password=hashed_password,
                created_at=datetime.now(),
            )

            await conn.execute(
                bind_params,
            )

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"사용자 등록 실패: {e}",
            ) from e

    async def sign_in(
        self, email: str, password: str, conn: AsyncConnection
    ) -> UserDataPass:
        user_vo = await self.get_user_vo_by_email(email, conn)
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
        return user_vo

    async def get_user_by_email(
        self, email: str, conn: AsyncConnection
    ) -> UserData | None:
        query = """
                    SELECT id, name, email
                    FROM user
                    WHERE email = :email
                """
        stmt = text(query)
        bind_params = stmt.bindparams(email=email)
        result = await conn.execute(bind_params)
        user_vo = result.fetchone()

        if user_vo:
            return UserData(
                id=user_vo.id,
                name=user_vo.name,
                email=user_vo.email,
            )
        return None

    async def get_user_vo_by_email(
        self, email: str, conn: AsyncConnection
    ) -> UserDataPass | None:
        query = """
                    SELECT id, name, email, hashed_password, created_at
                    FROM user
                    WHERE email = :email
                """
        stmt = text(query)
        bind_params = stmt.bindparams(email=email)
        result = await conn.execute(bind_params)
        user_vo = result.fetchone()

        if user_vo:
            return UserDataPass(
                id=user_vo.id,
                name=user_vo.name,
                email=user_vo.email,
                hashed_password=user_vo.hashed_password,
                created_at=user_vo.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        return None

import os
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 데이터베이스 커넥션 풀(Connection Pool) 설정을 위한 옵션입니다.
# 커넥션 풀은 데이터베이스 연결을 미리 만들어두고 재사용하여 성능을 향상시킵니다.
DB_CONNECTION_OPTIONS: dict[str, Any] = {
    "pool_size": 30,  # 풀에서 유지할 최소한의 커넥션 수
    "max_overflow": 10,  # 풀 크기를 초과하여 생성할 수 있는 임시 커넥션 수
    "pool_recycle": 300,  # 커넥션을 재사용하기 전 최대 유지 시간(초). 이 시간이 지나면 재연결합니다.
}

DB_SESSION_OPTIONS: dict[str, Any] = {
    "expire_on_commit": False,
    "autocommit": False,
    "class_": AsyncSession,
}


# 데이터베이스 연결 및 세션 관리를 책임지는 클래스입니다.
class MysqlDatabase:
    def __init__(
        self,
        db_url: str,
        options: dict[str, Any] | None = None,
        session_options: dict[str, Any] | None = None,
    ):
        if not db_url:
            raise ValueError("DATABASE_URL is not set")
        # create_async_engine: SQLAlchemy의 비동기 엔진을 생성합니다.
        # 이 엔진은 실제 데이터베이스 연결 및 통신을 담당합니다.
        self.engine = create_async_engine(db_url, **(options or {}))

        # async_sessionmaker: 비동기 세션(AsyncSession)을 생성하는 팩토리(공장)입니다.
        # 이 팩토리를 통해 일관된 설정의 세션을 쉽게 만들 수 있습니다.
        self.async_session_maker = async_sessionmaker(
            self.engine, **(session_options or {})
        )

    # Raw 쿼리 실행을 위한 기존의 연결 방식입니다. ORM으로 전환하면서 더 이상 사용하지 않을 수 있습니다.
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        conn: AsyncConnection | None = None
        transaction = None

        try:
            # 엔진으로부터 직접 커넥션을 얻고 트랜잭션을 시작합니다.
            conn = await self.engine.connect()
            transaction = await conn.begin()
            yield conn  # FastAPI 의존성 주입을 통해 이 커넥션을 라우터에 전달
            if transaction:
                await transaction.commit()  # 요청 처리가 성공적으로 끝나면 커밋
        except Exception as e:
            if transaction:
                await transaction.rollback()  # 오류 발생 시 롤백

            if isinstance(e, SQLAlchemyError):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=str(e),
                ) from e
            else:
                raise HTTPException(status_code=500, detail=str(e)) from e
        finally:
            if conn:
                await conn.close()  # 작업이 끝나면 커넥션을 풀에 반환

    # ORM을 사용하기 위한 비동기 세션을 생성하고 제공하는 메서드입니다.
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession | None = None
        try:
            # 세션 팩토리를 호출하여 새로운 세션을 생성합니다.
            session = self.async_session_maker()
            yield session  # FastAPI 의존성 주입을 통해 이 세션을 서비스 계층이나 라우터에 전달
            await session.commit()  # 요청 처리가 성공적으로 끝나면 커밋
        except Exception as e:
            if session:
                await session.rollback()  # 오류 발생 시 롤백

            if isinstance(e, SQLAlchemyError):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=str(e),
                ) from e
            else:
                raise HTTPException(status_code=500, detail=str(e)) from e
        finally:
            if session:
                await session.close()  # 작업이 끝나면 세션을 닫음


# 환경 변수에서 데이터베이스 접속 정보를 가져옵니다.
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# MysqlDatabase 클래스의 인스턴스를 생성합니다. 이 인스턴스는 애플리케이션 전체에서 공유됩니다.
db = MysqlDatabase(database_url, DB_CONNECTION_OPTIONS, DB_SESSION_OPTIONS)

# FastAPI의 Depends()에서 사용하기 쉽도록 메서드를 변수로 할당합니다.
get_connection_db = db.get_connection  # 레거시 연결 방식
get_db_session = db.get_session  # ORM 세션 방식

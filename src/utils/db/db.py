import os
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

DB_CONNECTION_OPTIONS: dict[str, Any] = {
    "pool_size": 30,
    "max_overflow": 10,
    "pool_recycle": 300,
}


class MysqlDatabase:
    def __init__(self, db_url: str, options: dict[str, dict] | None = None):
        if not db_url:
            raise ValueError("DATABASE_URL is not set")
        self.engine = create_async_engine(db_url, **(options or {}))

    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        conn: AsyncConnection | None = None
        transaction = None

        try:
            conn = await self.engine.connect()
            transaction = await conn.begin()
            yield conn
            if transaction:
                await transaction.commit()
        except Exception as e:
            if transaction:
                await transaction.rollback()

            if isinstance(e, SQLAlchemyError):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=str(e),
                ) from e
            else:
                raise HTTPException(status_code=500, detail=str(e)) from e
        finally:
            if conn:
                await conn.close()


database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

db = MysqlDatabase(database_url, DB_CONNECTION_OPTIONS)

get_connection_db = db.get_connection

import os
from collections.abc import Generator
from typing import Any

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

DB_CONNECTION_OPTIONS: dict[str, Any] = {
    "pool_size": 30,
    "max_overflow": 10,
    "echo_pool": True,
}


class PostgreDatabase:
    def __init__(self, db_url: str, options: dict[str, dict] | None = None):
        if not db_url:
            raise ValueError("DATABASE_URL is not set")
        self.engine = create_engine(db_url, **(options or {}))

    def get_connection(self) -> Generator[Connection, None, None]:
        conn = None
        try:
            conn = self.engine.connect()
            yield conn
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e)) from e
        finally:
            if conn:
                conn.close()


database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

db = PostgreDatabase(database_url, DB_CONNECTION_OPTIONS)

get_connection_db = db.get_connection

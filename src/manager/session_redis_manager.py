import json

from src.utils.db.redis import redis_db


class SessionRedisManager:
    def __init__(self) -> None:
        self.redis_db = redis_db
        self.session_expire_time = 60 * 60

    async def _get_redis_session(self, session_id: str) -> dict | None:
        redis_key = f"session:{session_id}"
        session_data_byte = await self.redis_db.get_client().get(redis_key)

        if session_data_byte:
            await self.redis_db.get_client().expire(redis_key, self.session_expire_time)
            data = json.loads(session_data_byte)
            if isinstance(data, dict):
                return data
        return None

    async def _set_redis_session(self, session_id: str, session_data: dict) -> None:
        redis_key = f"session:{session_id}"
        json_value = json.dumps(session_data)
        await self.redis_db.get_client().setex(
            name=redis_key,
            value=json_value,
            time=self.session_expire_time,
        )

    async def _delete_redis_session(self, session_id: str) -> None:
        redis_key = f"session:{session_id}"
        await self.redis_db.get_client().delete(redis_key)

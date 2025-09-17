import uuid
from datetime import timedelta

from src.utils.db.redis import redis_db


class EmailVerificationTokenManager:
    PREFIX = "email_verify"

    def __init__(self) -> None:
        self._redis = redis_db.get_client()

    @staticmethod
    def generate_token() -> str:
        return uuid.uuid4().hex

    def _key(self, token: str) -> str:
        return f"{self.PREFIX}:{token}"

    async def save_token(self, token: str, user_id: int, ttl: timedelta) -> None:
        await self._redis.setex(
            self._key(token), int(ttl.total_seconds()), str(user_id)
        )

    async def pop_user_id(self, token: str) -> int | None:
        key = self._key(token)
        user_id_str = await self._redis.get(key)
        if user_id_str is None:
            return None
        await self._redis.delete(key)
        try:
            return int(user_id_str)
        except ValueError:
            return None

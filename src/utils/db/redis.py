import os
from typing import Any

from redis.asyncio import Redis


class RedisDatabase:
    _instance: "RedisDatabase | None" = None
    redis: Redis

    def __new__(cls, options: dict[str, Any] | None = None) -> "RedisDatabase":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                raise ValueError("REDIS_URL is not set")
            cls._instance.redis = Redis.from_url(redis_url, **(options or {}))
        return cls._instance

    def get_client(self) -> Redis:
        return self.redis


redis_options = {"decode_responses": True, "max_connections": 10}
redis_db = RedisDatabase(redis_options)

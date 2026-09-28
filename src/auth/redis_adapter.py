import redis
from datetime import datetime, timezone

from settings import RedisSettings
from src.auth.ports import TokenRepository


class RedisTokenRepository(TokenRepository):
    def __init__(self, settings: RedisSettings):
        self.redis = redis.Redis(
            host=settings.host,
            port=settings.port,
            db=settings.db,
            password=settings.password,
            ssl=settings.ssl,
            socket_connect_timeout=settings.timeout,
            decode_responses=True,
        )

        self.prefix = settings.prefix if hasattr(settings, "prefix") else "token"

    def _make_key(self, token: str) -> str:
        return f"{self.prefix}:{token}" if self.prefix else token

    def save_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        ttl = int((expires_at - datetime.now(tz=timezone.utc)).total_seconds())
        key = self._make_key(token)
        self.redis.set(key, str(user_id), ex=ttl)

    def get_token(self, token: str) -> int | None:
        key = self._make_key(token)
        user_id = self.redis.get(key)
        if user_id is None:
            return None
        return int(user_id)

    def revoke_token(self, token: str) -> None:
        key = self._make_key(token)
        self.redis.delete(key)

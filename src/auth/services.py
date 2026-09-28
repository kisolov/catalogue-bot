import jwt
from datetime import datetime, timedelta, timezone

from src.auth.ports import TokenRepository
from settings import JWTSettings
from src.shared.exceptions import TokenExpiredException, InvalidTokenException


class TokenService:
    def __init__(self, repo: TokenRepository, jwt_settings: JWTSettings):
        self.repo = repo
        self.settings = jwt_settings

    def create_token(self, user_id: int, expires_minutes: int | None = None) -> str:
        expires_minutes = expires_minutes or self.settings.access_token_expires_minutes
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
        payload = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(
            payload, self.settings.secret_key, algorithm=self.settings.algorithm
        )

        self.repo.save_token(user_id, token, expire)
        return token

    def verify_token(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token, self.settings.secret_key, algorithms=[self.settings.algorithm]
            )
            int(payload["sub"])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
            raise InvalidTokenException()

        stored_user_id = self.repo.get_token(token)
        if stored_user_id is None:
            raise InvalidTokenException()
        return stored_user_id

    def revoke_token(self, token: str) -> None:
        self.repo.revoke_token(token)

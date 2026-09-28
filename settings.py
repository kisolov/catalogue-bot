from typing import List, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    allowed_origins: List[str]
    port: int
    host: str
    forwarded_allow_ips: str = "127.0.0.1"

    model_config = SettingsConfigDict(
        env_prefix="SERVER_", extra="ignore", env_file=".env"
    )


class DatabaseSettings(BaseSettings):
    provider: str
    host: str = "localhost"
    port: int = 5432
    user: str
    password: SecretStr | None
    name: str
    schema: str
    pool_min_size: int = 5
    pool_max_size: int = 20
    ssl: bool = False
    timeout: int = 30
    migrations_path: str = "migrations/sql/db.sql"

    model_config = SettingsConfigDict(
        env_prefix="DB_", extra="ignore", env_file=".env"
    )


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    timeout: int = 30
    prefix: str = "app:"

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", extra="ignore", env_file=".env"
    )


class JWTSettings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 60 * 24

    model_config = SettingsConfigDict(
        env_prefix="JWT_", extra="ignore", env_file=".env"
    )


class TelegramSettings(BaseSettings):
    bot_token: SecretStr
    init_data_max_age_seconds: int = 60 * 60 * 24

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_", extra="ignore", env_file=".env"
    )

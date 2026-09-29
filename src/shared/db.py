from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings import DatabaseSettings

STATEMENT_SEPARATOR = "-- STATEMENT-END"


class Database:
    """Async-движок PostgreSQL, транзакции адаптеров и раннер SQL-миграций.

    Конструктор ничего не подключает: соединения открываются лениво, поэтому
    объект безопасно создавать в DI-контейнере синхронно."""

    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self.engine: AsyncEngine = create_async_engine(
            self._url(),
            pool_size=settings.pool_min_size,
            max_overflow=max(settings.pool_max_size - settings.pool_min_size, 0),
            pool_pre_ping=True,
            connect_args={
                "timeout": settings.timeout,
                "server_settings": {"search_path": settings.schema},
            },
        )
        self._sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    def _url(self) -> URL:
        password = self.settings.password
        return URL.create(
            "postgresql+asyncpg",
            username=self.settings.user,
            password=password.get_secret_value() if password else None,
            host=self.settings.host,
            port=self.settings.port,
            database=self.settings.name,
        )

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """Одна транзакция на операцию адаптера: коммит при выходе, откат при
        исключении (в том числе доменном)."""
        async with self._sessions() as session, session.begin():
            yield session

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def migrate(self) -> None:
        migrations_path = Path(self.settings.migrations_path).parent
        sql_files = sorted(f.name for f in migrations_path.glob("*.sql"))

        async with self.engine.connect() as conn:
            raw = (await conn.get_raw_connection()).driver_connection
            # Сырое соединение asyncpg выполняет несколько команд разом
            # (тела функций с `;` внутри $BODY$), в отличие от prepared statement.
            async with raw.transaction():
                await raw.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    "name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT now())"
                )
                applied = {
                    row["name"]
                    for row in await raw.fetch("SELECT name FROM schema_migrations")
                }
                if not applied and await raw.fetchval(
                    "SELECT to_regclass('users') IS NOT NULL"
                ):
                    # База создана до появления учёта миграций: схема уже есть.
                    applied = {"db.sql"}
                    await raw.execute(
                        "INSERT INTO schema_migrations (name) VALUES ($1)", "db.sql"
                    )

                for file_name in sql_files:
                    if file_name in applied:
                        continue
                    content = (migrations_path / file_name).read_text(encoding="utf-8")
                    for stmt in content.split(STATEMENT_SEPARATOR):
                        if stmt.strip():
                            await raw.execute(stmt.strip())
                    await raw.execute(
                        "INSERT INTO schema_migrations (name) VALUES ($1)", file_name
                    )

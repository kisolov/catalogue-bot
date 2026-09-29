from src.shared.db import Database


class TestDatabase(Database):
    async def reset(self) -> None:
        """Чистая схема с применёнными миграциями."""
        schema = self.settings.schema
        async with self.engine.begin() as conn:
            await conn.exec_driver_sql(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
            await conn.exec_driver_sql(f"CREATE SCHEMA {schema}")
        await self.migrate()

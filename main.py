import asyncio

from di import container
from src.bootstrap.server_factory import ServerFactory


async def run_server() -> None:
    # fail-fast: обязательные настройки читаем до старта, а не на первом запросе
    for settings in (
        container.db_settings,
        container.redis_settings,
        container.jwt_settings,
        container.telegram_settings,
    ):
        settings()
    database = container.database()
    await database.migrate()
    try:
        server = ServerFactory(container.server_settings()).create_server()
        await server.serve()
    finally:
        await container.token_repo().close()
        await database.dispose()


if __name__ == "__main__":
    asyncio.run(run_server())

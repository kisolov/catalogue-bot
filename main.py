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
    container.init_resources()
    try:
        server = ServerFactory(container.server_settings()).create_server()
        await server.serve()
    finally:
        container.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(run_server())

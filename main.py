import asyncio

from di import container
from src.bootstrap.server_factory import ServerFactory


async def run_server() -> None:
    container.init_resources()
    try:
        server = ServerFactory(container.server_settings()).create_server()
        await server.serve()
    finally:
        container.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(run_server())

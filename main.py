import asyncio
import sys

from dependency_injector.wiring import Provide, inject

import settings
from di import container, Container
from src.bootstrap.server_factory import ServerFactory


@inject
async def run_server(
    server_config: settings.ServerSettings = Provide[Container.server_config],
):
    await container.init_resources()
    try:
        server = ServerFactory(server_config).create_server()
        await server.serve()
    finally:
        await container.shutdown_resources()


if __name__ == "__main__":
    container.wire(modules=[sys.modules[__name__]])
    asyncio.run(run_server())

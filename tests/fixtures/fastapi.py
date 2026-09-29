import pytest

import httpx

from src.bootstrap import ServerFactory


class FastAPIFixtures:
    @pytest.fixture
    async def fastapi_client(self, container):
        server_factory = ServerFactory(container.server_settings())

        app = server_factory._configure_app()
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            yield client

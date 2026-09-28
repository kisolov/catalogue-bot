import pytest

from fastapi.testclient import TestClient

from src.bootstrap import ServerFactory


class FastAPIFixtures:
    @pytest.fixture
    def fastapi_client(self, container):
        server_factory = ServerFactory(container.server_settings())

        app = server_factory._configure_app()
        return TestClient(app)

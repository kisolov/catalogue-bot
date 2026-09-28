from tests.cases.base import BaseTestGroup


class TestHealth(BaseTestGroup):
    async def test_health_is_public(self, fastapi_client):
        response = fastapi_client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestHttpHardening(BaseTestGroup):
    async def test_docs_can_be_disabled(self):
        from fastapi.testclient import TestClient

        from src.bootstrap.server_factory import ServerFactory

        settings = self.container.server_settings()
        settings = settings.model_copy(update={"docs_enabled": False})
        app = ServerFactory(settings)._configure_app()

        client = TestClient(app)

        assert client.get("/api/docs").status_code == 404
        assert client.get("/api/openapi.json").status_code == 404

    async def test_cors_does_not_allow_credentials(self, fastapi_client):
        response = fastapi_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert "access-control-allow-credentials" not in response.headers

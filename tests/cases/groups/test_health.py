from tests.cases.base import BaseTestGroup


class TestHealth(BaseTestGroup):
    async def test_health_is_public(self, fastapi_client):
        response = await fastapi_client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestHttpHardening(BaseTestGroup):
    async def test_docs_can_be_disabled(self):
        import httpx

        from src.bootstrap.server_factory import ServerFactory

        settings = self.container.server_settings()
        settings = settings.model_copy(update={"docs_enabled": False})
        app = ServerFactory(settings)._configure_app()

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            assert (await client.get("/api/docs")).status_code == 404
            assert (await client.get("/api/openapi.json")).status_code == 404

    async def test_cors_does_not_allow_credentials(self, fastapi_client):
        response = await fastapi_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert "access-control-allow-credentials" not in response.headers

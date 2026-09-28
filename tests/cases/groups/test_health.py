from tests.cases.base import BaseTestGroup


class TestHealth(BaseTestGroup):
    async def test_health_is_public(self, fastapi_client):
        response = fastapi_client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

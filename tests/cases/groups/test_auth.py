import time

from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures
from tests.utils.telegram import build_init_data


class TestTelegramAuth(BaseTestGroup, ModelsFixtures):
    def _login(self, client, init_data):
        return client.post("/api/auth/telegram", json={"init_data": init_data})

    async def test_first_login_creates_user_and_returns_working_token(
        self, fastapi_client
    ):
        response = self._login(fastapi_client, build_init_data(user_id=777001))

        assert response.status_code == 200
        body = response.json()
        assert body["user"]["telegram_id"] == 777001
        assert body["user"]["role"] == "user"
        me = fastapi_client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"}
        )
        assert me.status_code == 200
        assert me.json()["id"] == body["user"]["id"]

    async def test_repeat_login_reuses_user(self, fastapi_client):
        first = self._login(fastapi_client, build_init_data(user_id=777002)).json()
        second = self._login(fastapi_client, build_init_data(user_id=777002)).json()

        assert first["user"]["id"] == second["user"]["id"]

    async def test_existing_admin_keeps_role(self, user_factory, fastapi_client):
        from src.users.models import UserRole

        admin = user_factory.create(telegram_id=777003, role=UserRole.ADMIN)

        body = self._login(fastapi_client, build_init_data(user_id=777003)).json()

        assert body["user"]["id"] == admin.id
        assert body["user"]["role"] == "admin"

    async def test_wrong_bot_token_rejected(self, fastapi_client):
        response = self._login(
            fastapi_client, build_init_data(user_id=1, bot_token="1:OTHER")
        )

        assert response.status_code == 401

    async def test_tampered_payload_rejected(self, fastapi_client):
        init_data = build_init_data(user_id=1).replace("Ivan", "Evil")

        assert self._login(fastapi_client, init_data).status_code == 401

    async def test_missing_hash_rejected(self, fastapi_client):
        response = self._login(fastapi_client, "auth_date=1&user=%7B%7D")

        assert response.status_code == 401

    async def test_expired_init_data_rejected(self, fastapi_client):
        old = build_init_data(user_id=1, auth_date=int(time.time()) - 60 * 60 * 25)

        assert self._login(fastapi_client, old).status_code == 401

    async def test_garbage_rejected(self, fastapi_client):
        assert self._login(fastapi_client, "not-init-data").status_code == 401

    async def test_logout_revokes_token(self, sample_user, auth_headers, fastapi_client):
        assert fastapi_client.get("/api/auth/me", headers=auth_headers).status_code == 200

        assert fastapi_client.post("/api/auth/logout", headers=auth_headers).status_code == 204

        assert fastapi_client.get("/api/auth/me", headers=auth_headers).status_code == 401

    async def test_logout_requires_auth(self, fastapi_client):
        assert fastapi_client.post("/api/auth/logout").status_code == 401

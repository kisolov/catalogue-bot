import pytest

from src.users.models import User, UserRole
from src.users.schema import CreateUserRequest
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestUsersEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_create_user_success(self, admin_auth_headers, fastapi_client):
        request_data = CreateUserRequest(
            telegram_id=101010,
            role=UserRole.USER,
        )
        response = fastapi_client.post(
            "/api/users/",
            json=request_data.model_dump(),
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["telegram_id"] == request_data.telegram_id
        assert response_data["role"] == request_data.role.value

    async def test_create_user_with_admin_role(
        self, admin_auth_headers, fastapi_client
    ):
        request_data = CreateUserRequest(
            telegram_id=202020,
            role=UserRole.ADMIN,
        )
        response = fastapi_client.post(
            "/api/users/",
            json=request_data.model_dump(),
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["role"] == UserRole.ADMIN.value

    async def test_create_user_unauthorized(self, fastapi_client):
        response = fastapi_client.post("/api/users/", json={"telegram_id": 1})

        assert response.status_code == 401

    async def test_create_user_forbidden_for_regular_user(
        self, auth_headers, fastapi_client
    ):
        response = fastapi_client.post(
            "/api/users/",
            json={"telegram_id": 1, "role": "admin"},
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_create_user_duplicate_telegram_id(
        self, sample_user, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.post(
            "/api/users/",
            json={"telegram_id": sample_user.telegram_id},
            headers=admin_auth_headers,
        )

        assert response.status_code == 409

    async def test_get_user_by_id_success(self, sample_user, admin_auth_headers, fastapi_client):
        response = fastapi_client.get(
            f"/api/users/{sample_user.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == sample_user.id
        assert response_data["telegram_id"] == sample_user.telegram_id

    async def test_get_user_by_id_unauthorized(self, sample_user, fastapi_client):
        response = fastapi_client.get(f"/api/users/{sample_user.id}")

        assert response.status_code == 401

    async def test_get_user_by_id_forbidden(self, sample_user, auth_headers, fastapi_client):
        response = fastapi_client.get(
            f"/api/users/{sample_user.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_get_user_by_telegram_id_success(
        self, sample_user, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.get(
            f"/api/users/by_telegram/{sample_user.telegram_id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == sample_user.id
        assert response_data["telegram_id"] == sample_user.telegram_id

    async def test_get_user_by_telegram_id_unauthorized(
        self, sample_user, fastapi_client
    ):
        response = fastapi_client.get(
            f"/api/users/by_telegram/{sample_user.telegram_id}"
        )

        assert response.status_code == 401

    async def test_get_user_by_telegram_id_forbidden(
        self, sample_user, auth_headers, fastapi_client
    ):
        response = fastapi_client.get(
            f"/api/users/by_telegram/{sample_user.telegram_id}",
            headers=auth_headers,
        )

        assert response.status_code == 403

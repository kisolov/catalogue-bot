from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestCategoriesEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_list_categories_is_public(self, sample_category, fastapi_client):
        response = fastapi_client.get("/api/categories/")

        assert response.status_code == 200
        assert sample_category.id in [c["id"] for c in response.json()]

    async def test_get_category_not_found(self, fastapi_client):
        assert fastapi_client.get("/api/categories/99999").status_code == 404

    async def test_create_category_success(self, admin_auth_headers, fastapi_client):
        response = fastapi_client.post(
            "/api/categories/",
            json={"name": "Посуда", "slug": "dishes"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["slug"] == "dishes"

    async def test_create_category_requires_admin(self, auth_headers, fastapi_client):
        payload = {"name": "Посуда", "slug": "dishes"}

        assert fastapi_client.post("/api/categories/", json=payload).status_code == 401
        assert (
            fastapi_client.post(
                "/api/categories/", json=payload, headers=auth_headers
            ).status_code
            == 403
        )

    async def test_create_category_duplicate_slug(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.post(
            "/api/categories/",
            json={"name": "Дубль", "slug": sample_category.slug},
            headers=admin_auth_headers,
        )

        assert response.status_code == 409

    async def test_update_category_success(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.patch(
            f"/api/categories/{sample_category.id}",
            json={"name": "Новое имя"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Новое имя"

    async def test_delete_empty_category(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.delete(
            f"/api/categories/{sample_category.id}", headers=admin_auth_headers
        )

        assert response.status_code == 204

    async def test_delete_category_with_products_is_rejected(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.delete(
            f"/api/categories/{sample_product.category_id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 409
        assert fastapi_client.get(f"/api/products/{sample_product.id}").status_code == 200

import pytest

from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestCategoriesEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_list_categories_is_public(self, sample_category, fastapi_client):
        response = await fastapi_client.get("/api/categories/")

        assert response.status_code == 200
        assert sample_category.id in [c["id"] for c in response.json()]

    async def test_get_category_not_found(self, fastapi_client):
        assert (await fastapi_client.get("/api/categories/99999")).status_code == 404

    async def test_create_category_success(self, admin_auth_headers, fastapi_client):
        response = await fastapi_client.post(
            "/api/categories/",
            json={"name": "Посуда", "slug": "dishes"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["slug"] == "dishes"

    async def test_create_category_requires_admin(self, auth_headers, fastapi_client):
        payload = {"name": "Посуда", "slug": "dishes"}

        assert (
            await fastapi_client.post("/api/categories/", json=payload)
        ).status_code == 401
        assert (
            await fastapi_client.post(
                "/api/categories/", json=payload, headers=auth_headers
            )
        ).status_code == 403

    async def test_create_category_duplicate_slug(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/categories/",
            json={"name": "Дубль", "slug": sample_category.slug},
            headers=admin_auth_headers,
        )

        assert response.status_code == 409

    async def test_update_category_success(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.patch(
            f"/api/categories/{sample_category.id}",
            json={"name": "Новое имя"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Новое имя"

    async def test_delete_empty_category(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.delete(
            f"/api/categories/{sample_category.id}", headers=admin_auth_headers
        )

        assert response.status_code == 204

    async def test_delete_category_with_products_is_rejected(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.delete(
            f"/api/categories/{sample_product.category_id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 409
        assert (
            await fastapi_client.get(f"/api/products/{sample_product.id}")
        ).status_code == 200


class TestCategoriesTree(BaseTestGroup, ModelsFixtures):
    async def test_create_with_missing_parent_is_404(
        self, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/categories/",
            json={"name": "Кружки", "slug": "mugs", "parent_id": 99999},
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    async def test_create_with_parent(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/categories/",
            json={"name": "Кружки", "slug": "mugs", "parent_id": sample_category.id},
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["parent_id"] == sample_category.id

    async def test_category_cannot_be_its_own_parent(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.patch(
            f"/api/categories/{sample_category.id}",
            json={"parent_id": sample_category.id},
            headers=admin_auth_headers,
        )

        assert response.status_code == 422

    async def test_category_cannot_move_under_its_descendant(
        self, admin_auth_headers, fastapi_client
    ):
        async def create(slug, parent_id=None):
            return (
                await fastapi_client.post(
                    "/api/categories/",
                    json={"name": slug, "slug": slug, "parent_id": parent_id},
                    headers=admin_auth_headers,
                )
            ).json()["id"]

        root = await create("root")
        child = await create("child", root)
        leaf = await create("leaf", child)

        response = await fastapi_client.patch(
            f"/api/categories/{root}",
            json={"parent_id": leaf},
            headers=admin_auth_headers,
        )

        assert response.status_code == 422

    async def test_parent_can_be_cleared(self, admin_auth_headers, fastapi_client):
        parent = (
            await fastapi_client.post(
                "/api/categories/",
                json={"name": "p", "slug": "p"},
                headers=admin_auth_headers,
            )
        ).json()["id"]
        child = (
            await fastapi_client.post(
                "/api/categories/",
                json={"name": "c", "slug": "c", "parent_id": parent},
                headers=admin_auth_headers,
            )
        ).json()["id"]

        response = await fastapi_client.patch(
            f"/api/categories/{child}",
            json={"parent_id": None},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["parent_id"] is None

    async def test_create_rejects_too_long_name(
        self, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/categories/",
            json={"name": "x" * 101, "slug": "long"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 422


class TestCategoriesPagination(BaseTestGroup, ModelsFixtures):
    async def test_pages_are_ordered_and_do_not_overlap(
        self, category_factory, fastapi_client
    ):
        created = [(await category_factory.create()).id for _ in range(3)]

        first = (await fastapi_client.get("/api/categories/?limit=2")).json()
        second = (await fastapi_client.get("/api/categories/?limit=2&offset=2")).json()

        assert [c["id"] for c in first + second] == created

    @pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
    async def test_invalid_paging_is_422(self, query, fastapi_client):
        assert (
            await fastapi_client.get(f"/api/categories/?{query}")
        ).status_code == 422

import asyncio

import pytest
from decimal import Decimal

from src.products.models import Product
from src.products.schema import UpdateProductRequest
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestProductsEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_list_products_success(self, product_factory, fastapi_client):
        product1 = await product_factory.create()
        product2 = await product_factory.create()

        response = await fastapi_client.get("/api/products/")

        assert response.status_code == 200
        products = response.json()
        assert len(products) >= 2
        product_ids = [p["id"] for p in products]
        assert product1.id in product_ids
        assert product2.id in product_ids

    async def test_get_product_by_id_success(self, sample_product, fastapi_client):
        response = await fastapi_client.get(f"/api/products/{sample_product.id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == sample_product.id
        assert response_data["name"] == sample_product.name
        assert float(response_data["price"]) == float(sample_product.price)

    async def test_get_product_by_id_not_found(self, fastapi_client):
        response = await fastapi_client.get("/api/products/99999")

        assert response.status_code == 404

    async def test_update_product_success(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        update_data = UpdateProductRequest(
            name="Updated Product Name",
            slug="updated-product-slug",
            price=Decimal("199.99"),
            stock=20,
            is_active=True,
            category_id=sample_product.category_id,
        )
        response = await fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json=update_data.model_dump(mode="json", exclude_unset=True),
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()

        assert response_data["name"] == update_data.name
        assert float(response_data["price"]) == float(update_data.price)
        assert response_data["stock"] == update_data.stock

    async def test_update_product_unauthorized(self, sample_product, fastapi_client):
        response = await fastapi_client.patch(
            f"/api/products/{sample_product.id}", json={"stock": 1}
        )

        assert response.status_code == 401

    async def test_update_product_forbidden_for_regular_user(
        self, sample_product, auth_headers, fastapi_client
    ):
        response = await fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"stock": 1},
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_update_product_partial_keeps_other_fields(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"stock": 7},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["stock"] == 7
        assert response.json()["slug"] == sample_product.slug

    async def test_create_product_success(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/products/",
            json={
                "name": "Кружка",
                "slug": "mug",
                "price": "12.50",
                "stock": 3,
                "is_active": True,
                "category_id": sample_category.id,
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["slug"] == "mug"

    async def test_create_product_duplicate_slug(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/products/",
            json={
                "name": "Другой",
                "slug": sample_product.slug,
                "price": "1.00",
                "stock": 1,
                "is_active": True,
                "category_id": sample_product.category_id,
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 409

    async def test_create_product_forbidden_for_regular_user(
        self, sample_category, auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/products/",
            json={
                "name": "x",
                "slug": "x",
                "price": "1.00",
                "stock": 1,
                "is_active": True,
                "category_id": sample_category.id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_delete_product_success(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.delete(
            f"/api/products/{sample_product.id}", headers=admin_auth_headers
        )

        assert response.status_code == 204
        assert (
            await fastapi_client.get(f"/api/products/{sample_product.id}")
        ).status_code == 404

    async def test_delete_product_forbidden_for_regular_user(
        self, sample_product, auth_headers, fastapi_client
    ):
        response = await fastapi_client.delete(
            f"/api/products/{sample_product.id}", headers=auth_headers
        )

        assert response.status_code == 403

    async def test_delete_product_not_found(self, admin_auth_headers, fastapi_client):
        response = await fastapi_client.delete(
            "/api/products/99999", headers=admin_auth_headers
        )

        assert response.status_code == 404

    async def test_list_products_filter_by_category(
        self, product_factory, category_factory, fastapi_client
    ):
        category = await category_factory.create()
        inside = await product_factory.create(category_id=category.id)
        await product_factory.create()

        response = await fastapi_client.get(f"/api/products/?category_id={category.id}")

        assert [p["id"] for p in response.json()] == [inside.id]

    async def test_create_products_without_sku_and_description(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        for slug in ("first", "second"):
            response = await fastapi_client.post(
                "/api/products/",
                json={
                    "name": slug,
                    "slug": slug,
                    "price": "1.00",
                    "stock": 1,
                    "is_active": True,
                    "category_id": sample_category.id,
                },
                headers=admin_auth_headers,
            )

            assert response.status_code == 201
            assert response.json()["sku"] is None


class TestProductsValidation(BaseTestGroup, ModelsFixtures):
    @staticmethod
    def _payload(category_id, **extra):
        return {
            "name": "Кружка",
            "slug": "mug",
            "price": "12.50",
            "stock": 3,
            "is_active": True,
            "category_id": category_id,
            **extra,
        }

    async def test_create_with_missing_category_is_404(
        self, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/products/",
            json=self._payload(99999),
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "extra",
        [
            {"price": "-1"},
            {"stock": -1},
            {"price": "100000000"},
            {"price": "1.234"},
            {"name": ""},
            {"sku": "x" * 51},
            {"stock": 2**31},
        ],
    )
    async def test_create_rejects_invalid_values(
        self, extra, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/products/",
            json=self._payload(sample_category.id, **extra),
            headers=admin_auth_headers,
        )

        assert response.status_code == 422

    async def test_create_rejects_compare_price_below_price(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.post(
            "/api/products/",
            json=self._payload(
                sample_category.id, price="10.00", compare_at_price="5.00"
            ),
            headers=admin_auth_headers,
        )

        assert response.status_code == 422

    async def test_update_rejects_negative_stock(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"stock": -5},
            headers=admin_auth_headers,
        )

        assert response.status_code == 422

    async def test_update_with_missing_category_is_404(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = await fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"category_id": 99999},
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    async def test_update_price_above_stored_compare_price_is_422(
        self, product_factory, admin_auth_headers, fastapi_client
    ):
        product = await product_factory.create(price="10.00", compare_at_price="20.00")

        response = await fastapi_client.patch(
            f"/api/products/{product.id}",
            json={"price": "30.00"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 422


class TestProductsPagination(BaseTestGroup, ModelsFixtures):
    async def test_pages_are_ordered_and_do_not_overlap(
        self, product_factory, fastapi_client
    ):
        created = [(await product_factory.create()).id for _ in range(5)]

        first = (await fastapi_client.get("/api/products/?limit=2&offset=0")).json()
        second = (await fastapi_client.get("/api/products/?limit=2&offset=2")).json()
        rest = (await fastapi_client.get("/api/products/?limit=2&offset=4")).json()

        ids = [p["id"] for p in first + second + rest]
        assert ids == created
        assert len(first) == len(second) == 2
        assert len(rest) == 1

    async def test_offset_past_the_end_is_empty(self, sample_product, fastapi_client):
        response = await fastapi_client.get("/api/products/?offset=1000")

        assert response.status_code == 200
        assert response.json() == []

    async def test_default_limit_is_applied(self, product_factory, fastapi_client):
        for _ in range(51):
            await product_factory.create()

        assert len((await fastapi_client.get("/api/products/")).json()) == 50

    @pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1", "limit=x"])
    async def test_invalid_paging_is_422(self, query, fastapi_client):
        assert (await fastapi_client.get(f"/api/products/?{query}")).status_code == 422


class TestProductsConcurrency(BaseTestGroup, ModelsFixtures):
    async def test_parallel_requests_beyond_pool_size_all_succeed(
        self, sample_product, fastapi_client
    ):
        responses = await asyncio.gather(
            *(fastapi_client.get("/api/products/") for _ in range(50))
        )

        assert {r.status_code for r in responses} == {200}

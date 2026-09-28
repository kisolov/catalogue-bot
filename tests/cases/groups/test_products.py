import pytest
from decimal import Decimal

from src.products.models import Product
from src.products.schema import UpdateProductRequest
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestProductsEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_list_products_success(self, product_factory, fastapi_client):
        product1 = product_factory.create()
        product2 = product_factory.create()

        response = fastapi_client.get("/api/products/")

        assert response.status_code == 200
        products = response.json()
        assert len(products) >= 2
        product_ids = [p["id"] for p in products]
        assert product1.id in product_ids
        assert product2.id in product_ids

    async def test_get_product_by_id_success(self, sample_product, fastapi_client):
        response = fastapi_client.get(f"/api/products/{sample_product.id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == sample_product.id
        assert response_data["name"] == sample_product.name
        assert float(response_data["price"]) == float(sample_product.price)

    async def test_get_product_by_id_not_found(self, fastapi_client):
        response = fastapi_client.get("/api/products/99999")

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
        response = fastapi_client.patch(
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
        response = fastapi_client.patch(
            f"/api/products/{sample_product.id}", json={"stock": 1}
        )

        assert response.status_code == 401

    async def test_update_product_forbidden_for_regular_user(
        self, sample_product, auth_headers, fastapi_client
    ):
        response = fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"stock": 1},
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_update_product_partial_keeps_other_fields(
        self, sample_product, admin_auth_headers, fastapi_client
    ):
        response = fastapi_client.patch(
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
        response = fastapi_client.post(
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
        response = fastapi_client.post(
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
        response = fastapi_client.post(
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
        response = fastapi_client.delete(
            f"/api/products/{sample_product.id}", headers=admin_auth_headers
        )

        assert response.status_code == 204
        assert (
            fastapi_client.get(f"/api/products/{sample_product.id}").status_code == 404
        )

    async def test_delete_product_forbidden_for_regular_user(
        self, sample_product, auth_headers, fastapi_client
    ):
        response = fastapi_client.delete(
            f"/api/products/{sample_product.id}", headers=auth_headers
        )

        assert response.status_code == 403

    async def test_delete_product_not_found(self, admin_auth_headers, fastapi_client):
        response = fastapi_client.delete(
            "/api/products/99999", headers=admin_auth_headers
        )

        assert response.status_code == 404

    async def test_list_products_filter_by_category(
        self, product_factory, category_factory, fastapi_client
    ):
        category = category_factory.create()
        inside = product_factory.create(category_id=category.id)
        product_factory.create()

        response = fastapi_client.get(f"/api/products/?category_id={category.id}")

        assert [p["id"] for p in response.json()] == [inside.id]

    async def test_create_products_without_sku_and_description(
        self, sample_category, admin_auth_headers, fastapi_client
    ):
        for slug in ("first", "second"):
            response = fastapi_client.post(
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

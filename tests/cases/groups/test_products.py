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

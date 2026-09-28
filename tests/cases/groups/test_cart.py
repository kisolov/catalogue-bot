import pytest

from src.cart.models import Cart, CartItem
from src.cart.schema import AddInCartRequest
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestCartEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_get_cart_success(
        self, sample_user, cart_factory, fastapi_client, container
    ):
        token_service = container.token_service()
        token = token_service.create_token(sample_user.id)
        auth_headers = {"Authorization": f"Bearer {token}"}

        cart = cart_factory.create(user_id=sample_user.id)

        response = fastapi_client.get(
            "/api/cart/products",
            headers=auth_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["user_id"] == cart.user_id
        assert len(response_data["items"]) > 0

    async def test_get_cart_unauthorized(self, fastapi_client):
        response = fastapi_client.get("/api/cart/products")

        assert response.status_code == 401

    async def test_add_to_cart_success(
        self, sample_user, sample_product, auth_headers, fastapi_client
    ):
        request_data = AddInCartRequest(
            product_id=sample_product.id,
            quantity=2,
        )

        response = fastapi_client.post(
            "/api/cart/products",
            json=request_data.model_dump(),
            headers=auth_headers,
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["product_id"] == sample_product.id
        assert response_data["quantity"] == 2

    async def test_add_to_cart_unauthorized(self, sample_product, fastapi_client):
        request_data = AddInCartRequest(
            product_id=sample_product.id,
            quantity=1,
        )

        response = fastapi_client.post(
            "/api/cart/products",
            json=request_data.model_dump(),
        )

        assert response.status_code == 401

    async def test_remove_from_cart_success(
        self, sample_user, cart_factory, auth_headers, fastapi_client
    ):
        cart = cart_factory.create(user_id=sample_user.id)
        product_id = cart.items[0].product_id

        response = fastapi_client.delete(
            f"/api/cart/products/{product_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    async def test_clear_cart_success(
        self, sample_user, cart_factory, auth_headers, fastapi_client
    ):
        cart_factory.create(user_id=sample_user.id)

        response = fastapi_client.delete(
            "/api/cart/products",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = fastapi_client.get(
            "/api/cart/products",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        assert len(get_response.json()["items"]) == 0


class TestCartQuantity(BaseTestGroup, ModelsFixtures):
    @pytest.mark.parametrize("quantity", [0, -1, 1001])
    async def test_quantity_out_of_range_is_422(
        self, quantity, sample_product, auth_headers, fastapi_client
    ):
        response = fastapi_client.post(
            "/api/cart/products",
            json={"product_id": sample_product.id, "quantity": quantity},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_adding_over_limit_to_existing_item_is_422(
        self, sample_product, auth_headers, fastapi_client
    ):
        payload = {"product_id": sample_product.id, "quantity": 600}
        first = fastapi_client.post(
            "/api/cart/products", json=payload, headers=auth_headers
        )

        second = fastapi_client.post(
            "/api/cart/products", json=payload, headers=auth_headers
        )

        assert first.status_code == 201
        assert second.status_code == 422

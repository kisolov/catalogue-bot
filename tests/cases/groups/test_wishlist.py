import pytest

from src.wishlist.models import Wishlist, Favorite
from src.wishlist.schema import AddInWishlistRequest
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestWishlistEndpoints(BaseTestGroup, ModelsFixtures):
    async def test_get_wishlist_success(
        self, sample_user, wishlist_factory, fastapi_client
    ):
        wishlist = wishlist_factory.create(user_id=sample_user.id)
        token_service = self.container.token_service()
        token = token_service.create_token(sample_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = fastapi_client.get(
            "/api/wishlist/products",
            headers=headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["user_id"] == wishlist.user_id
        assert len(response_data["products"]) > 0

    async def test_get_wishlist_unauthorized(self, fastapi_client):
        response = fastapi_client.get("/api/wishlist/products")

        assert response.status_code == 401

    async def test_add_to_wishlist_success(
        self, sample_user, sample_product, auth_headers, fastapi_client
    ):
        request_data = AddInWishlistRequest(product_id=sample_product.id)

        response = fastapi_client.post(
            "/api/wishlist/products",
            json=request_data.model_dump(),
            headers=auth_headers,
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["product_id"] == sample_product.id
        assert response_data["user_id"] == sample_user.id

    async def test_add_to_wishlist_unauthorized(self, sample_product, fastapi_client):
        request_data = AddInWishlistRequest(product_id=sample_product.id)

        response = fastapi_client.post(
            "/api/wishlist/products",
            json=request_data.model_dump(),
        )

        assert response.status_code == 401

    async def test_remove_from_wishlist_success(
        self, sample_user, wishlist_factory, fastapi_client
    ):
        wishlist = wishlist_factory.create(user_id=sample_user.id)
        product_id = wishlist.products[0].product_id
        token_service = self.container.token_service()
        token = token_service.create_token(sample_user.id)
        headers = {"Authorization": f"Bearer {token}"}

        response = fastapi_client.delete(
            f"/api/wishlist/products/{product_id}",
            headers=headers,
        )

        assert response.status_code == 204

        # Проверяем, что продукт удален
        get_response = fastapi_client.get(
            "/api/wishlist/products",
            headers=headers,
        )
        assert get_response.status_code == 200
        assert len(get_response.json()["products"]) == 0

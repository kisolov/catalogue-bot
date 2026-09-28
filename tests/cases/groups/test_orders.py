from decimal import Decimal

from src.cart.models import AddCartItemCmd
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestOrdersEndpoints(BaseTestGroup, ModelsFixtures):
    def _fill_cart(self, user, product, quantity):
        self.container.cart_service().add_item(
            AddCartItemCmd(user_id=user.id, product_id=product.id, quantity=quantity)
        )

    def _stock(self, product):
        return self.container.product_service().get_by_id(product.id).stock

    async def test_create_order_from_cart(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        first = product_factory.create(price=Decimal("10.00"), stock=5)
        second = product_factory.create(price=Decimal("2.50"), stock=5)
        self._fill_cart(sample_user, first, 2)
        self._fill_cart(sample_user, second, 4)

        response = fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "new"
        assert Decimal(body["total_price"]) == Decimal("30.00")
        assert sorted(i["quantity"] for i in body["items"]) == [2, 4]
        assert self._stock(first) == 3
        assert self._stock(second) == 1
        cart = fastapi_client.get("/api/cart/products", headers=auth_headers)
        assert cart.json()["items"] == []

    async def test_order_snapshots_price_and_name(
        self,
        sample_user,
        sample_product,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        self._fill_cart(sample_user, sample_product, 1)
        order = fastapi_client.post("/api/orders/", headers=auth_headers).json()

        fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"price": "999.00", "name": "renamed"},
            headers=admin_auth_headers,
        )
        again = fastapi_client.get(f"/api/orders/{order['id']}", headers=auth_headers)

        item = again.json()["items"][0]
        assert Decimal(item["price"]) == sample_product.price
        assert item["product_name"] == sample_product.name

    async def test_create_order_empty_cart(self, auth_headers, fastapi_client):
        response = fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 409

    async def test_create_order_insufficient_stock_changes_nothing(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        enough = product_factory.create(stock=10)
        scarce = product_factory.create(stock=1)
        self._fill_cart(sample_user, enough, 3)
        self._fill_cart(sample_user, scarce, 2)

        response = fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 409
        assert self._stock(enough) == 10
        assert self._stock(scarce) == 1
        cart = fastapi_client.get("/api/cart/products", headers=auth_headers)
        assert len(cart.json()["items"]) == 2
        assert fastapi_client.get("/api/orders/", headers=auth_headers).json() == []

    async def test_create_order_inactive_product(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        product = product_factory.create(is_active=False, stock=5)
        self._fill_cart(sample_user, product, 1)

        response = fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 409

    async def test_create_order_unauthorized(self, fastapi_client):
        assert fastapi_client.post("/api/orders/").status_code == 401

    async def test_list_returns_only_own_orders_newest_first(
        self, sample_user, order_factory, auth_headers, fastapi_client
    ):
        older = order_factory.create(user_id=sample_user.id)
        newer = order_factory.create(user_id=sample_user.id)
        order_factory.create()

        response = fastapi_client.get("/api/orders/", headers=auth_headers)

        assert [o["id"] for o in response.json()] == [newer.id, older.id]

    async def test_get_foreign_order_is_hidden(
        self, order_factory, auth_headers, fastapi_client
    ):
        foreign = order_factory.create()

        response = fastapi_client.get(f"/api/orders/{foreign.id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_admin_can_get_any_order(
        self, order_factory, admin_auth_headers, fastapi_client
    ):
        foreign = order_factory.create()

        response = fastapi_client.get(
            f"/api/orders/{foreign.id}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        assert response.json()["id"] == foreign.id

    async def test_admin_status_flow(
        self, order_factory, admin_auth_headers, fastapi_client
    ):
        order = order_factory.create()
        for new_status in ("processing", "shipped", "delivered"):
            response = fastapi_client.patch(
                f"/api/orders/{order.id}/status",
                json={"status": new_status},
                headers=admin_auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["status"] == new_status

    async def test_invalid_transition_rejected(
        self, order_factory, admin_auth_headers, fastapi_client
    ):
        order = order_factory.create()

        response = fastapi_client.patch(
            f"/api/orders/{order.id}/status",
            json={"status": "delivered"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 409

    async def test_status_change_requires_admin(
        self, sample_user, order_factory, auth_headers, fastapi_client
    ):
        order = order_factory.create(user_id=sample_user.id)

        response = fastapi_client.patch(
            f"/api/orders/{order.id}/status",
            json={"status": "processing"},
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_owner_cancel_restores_stock(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        product = product_factory.create(stock=5)
        self._fill_cart(sample_user, product, 3)
        order = fastapi_client.post("/api/orders/", headers=auth_headers).json()
        assert self._stock(product) == 2

        response = fastapi_client.post(
            f"/api/orders/{order['id']}/cancel", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
        assert self._stock(product) == 5

    async def test_owner_cannot_cancel_processing_order(
        self,
        sample_user,
        order_factory,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        order = order_factory.create(user_id=sample_user.id)
        fastapi_client.patch(
            f"/api/orders/{order.id}/status",
            json={"status": "processing"},
            headers=admin_auth_headers,
        )

        response = fastapi_client.post(
            f"/api/orders/{order.id}/cancel", headers=auth_headers
        )

        assert response.status_code == 409

    async def test_cancel_foreign_order_is_hidden(
        self, order_factory, auth_headers, fastapi_client
    ):
        foreign = order_factory.create()

        response = fastapi_client.post(
            f"/api/orders/{foreign.id}/cancel", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_admin_cancel_restores_stock(
        self,
        sample_user,
        product_factory,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        product = product_factory.create(stock=4)
        self._fill_cart(sample_user, product, 4)
        order = fastapi_client.post("/api/orders/", headers=auth_headers).json()

        fastapi_client.patch(
            f"/api/orders/{order['id']}/status",
            json={"status": "cancelled"},
            headers=admin_auth_headers,
        )

        assert self._stock(product) == 4

    async def test_delete_product_used_in_order_is_rejected(
        self,
        sample_user,
        sample_product,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        self._fill_cart(sample_user, sample_product, 1)
        fastapi_client.post("/api/orders/", headers=auth_headers)

        response = fastapi_client.delete(
            f"/api/products/{sample_product.id}", headers=admin_auth_headers
        )

        assert response.status_code == 409

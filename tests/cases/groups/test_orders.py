import asyncio

import pytest
from decimal import Decimal

from sqlalchemy import update

from src.cart.models import AddCartItemCmd
from src.shared.exceptions import InsufficientStockException
from src.shared.orm.models import ProductRow
from tests.cases.base import BaseTestGroup
from tests.fixtures.models import ModelsFixtures


class TestOrdersEndpoints(BaseTestGroup, ModelsFixtures):
    async def _fill_cart(self, user, product, quantity):
        await self.container.cart_service().add_item(
            AddCartItemCmd(user_id=user.id, product_id=product.id, quantity=quantity)
        )

    async def _stock(self, product):
        return (await self.container.product_service().get_by_id(product.id)).stock

    async def test_create_order_from_cart(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        first = await product_factory.create(price=Decimal("10.00"), stock=5)
        second = await product_factory.create(price=Decimal("2.50"), stock=5)
        await self._fill_cart(sample_user, first, 2)
        await self._fill_cart(sample_user, second, 4)

        response = await fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "new"
        assert Decimal(body["total_price"]) == Decimal("30.00")
        assert sorted(i["quantity"] for i in body["items"]) == [2, 4]
        assert await self._stock(first) == 3
        assert await self._stock(second) == 1
        cart = await fastapi_client.get("/api/cart/products", headers=auth_headers)
        assert cart.json()["items"] == []

    async def test_order_snapshots_price_and_name(
        self,
        sample_user,
        sample_product,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        await self._fill_cart(sample_user, sample_product, 1)
        order = (await fastapi_client.post("/api/orders/", headers=auth_headers)).json()

        await fastapi_client.patch(
            f"/api/products/{sample_product.id}",
            json={"price": "999.00", "name": "renamed"},
            headers=admin_auth_headers,
        )
        again = await fastapi_client.get(
            f"/api/orders/{order['id']}", headers=auth_headers
        )

        item = again.json()["items"][0]
        assert Decimal(item["price"]) == sample_product.price
        assert item["product_name"] == sample_product.name

    async def test_create_order_empty_cart(self, auth_headers, fastapi_client):
        response = await fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 409

    async def test_create_order_insufficient_stock_changes_nothing(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        enough = await product_factory.create(stock=10)
        scarce = await product_factory.create(stock=1)
        await self._fill_cart(sample_user, enough, 3)
        await self._fill_cart(sample_user, scarce, 2)

        response = await fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 409
        assert await self._stock(enough) == 10
        assert await self._stock(scarce) == 1
        cart = await fastapi_client.get("/api/cart/products", headers=auth_headers)
        assert len(cart.json()["items"]) == 2
        assert (
            await fastapi_client.get("/api/orders/", headers=auth_headers)
        ).json() == []

    async def test_create_order_inactive_product(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        product = await product_factory.create(is_active=False, stock=5)
        await self._fill_cart(sample_user, product, 1)

        response = await fastapi_client.post("/api/orders/", headers=auth_headers)

        assert response.status_code == 409

    async def test_create_order_unauthorized(self, fastapi_client):
        assert (await fastapi_client.post("/api/orders/")).status_code == 401

    async def test_list_returns_only_own_orders_newest_first(
        self, sample_user, order_factory, auth_headers, fastapi_client
    ):
        older = await order_factory.create(user_id=sample_user.id)
        newer = await order_factory.create(user_id=sample_user.id)
        await order_factory.create()

        response = await fastapi_client.get("/api/orders/", headers=auth_headers)

        assert [o["id"] for o in response.json()] == [newer.id, older.id]

    async def test_get_foreign_order_is_hidden(
        self, order_factory, auth_headers, fastapi_client
    ):
        foreign = await order_factory.create()

        response = await fastapi_client.get(
            f"/api/orders/{foreign.id}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_admin_can_get_any_order(
        self, order_factory, admin_auth_headers, fastapi_client
    ):
        foreign = await order_factory.create()

        response = await fastapi_client.get(
            f"/api/orders/{foreign.id}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        assert response.json()["id"] == foreign.id

    async def test_admin_status_flow(
        self, order_factory, admin_auth_headers, fastapi_client
    ):
        order = await order_factory.create()
        for new_status in ("processing", "shipped", "delivered"):
            response = await fastapi_client.patch(
                f"/api/orders/{order.id}/status",
                json={"status": new_status},
                headers=admin_auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["status"] == new_status

    async def test_invalid_transition_rejected(
        self, order_factory, admin_auth_headers, fastapi_client
    ):
        order = await order_factory.create()

        response = await fastapi_client.patch(
            f"/api/orders/{order.id}/status",
            json={"status": "delivered"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 409

    async def test_status_change_requires_admin(
        self, sample_user, order_factory, auth_headers, fastapi_client
    ):
        order = await order_factory.create(user_id=sample_user.id)

        response = await fastapi_client.patch(
            f"/api/orders/{order.id}/status",
            json={"status": "processing"},
            headers=auth_headers,
        )

        assert response.status_code == 403

    async def test_owner_cancel_restores_stock(
        self, sample_user, product_factory, auth_headers, fastapi_client
    ):
        product = await product_factory.create(stock=5)
        await self._fill_cart(sample_user, product, 3)
        order = (await fastapi_client.post("/api/orders/", headers=auth_headers)).json()
        assert await self._stock(product) == 2

        response = await fastapi_client.post(
            f"/api/orders/{order['id']}/cancel", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
        assert await self._stock(product) == 5

    async def test_owner_cannot_cancel_processing_order(
        self,
        sample_user,
        order_factory,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        order = await order_factory.create(user_id=sample_user.id)
        await fastapi_client.patch(
            f"/api/orders/{order.id}/status",
            json={"status": "processing"},
            headers=admin_auth_headers,
        )

        response = await fastapi_client.post(
            f"/api/orders/{order.id}/cancel", headers=auth_headers
        )

        assert response.status_code == 409

    async def test_cancel_foreign_order_is_hidden(
        self, order_factory, auth_headers, fastapi_client
    ):
        foreign = await order_factory.create()

        response = await fastapi_client.post(
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
        product = await product_factory.create(stock=4)
        await self._fill_cart(sample_user, product, 4)
        order = (await fastapi_client.post("/api/orders/", headers=auth_headers)).json()

        await fastapi_client.patch(
            f"/api/orders/{order['id']}/status",
            json={"status": "cancelled"},
            headers=admin_auth_headers,
        )

        assert await self._stock(product) == 4

    async def test_delete_product_used_in_order_is_rejected(
        self,
        sample_user,
        sample_product,
        auth_headers,
        admin_auth_headers,
        fastapi_client,
    ):
        await self._fill_cart(sample_user, sample_product, 1)
        await fastapi_client.post("/api/orders/", headers=auth_headers)

        response = await fastapi_client.delete(
            f"/api/products/{sample_product.id}", headers=admin_auth_headers
        )

        assert response.status_code == 409


class TestOrdersPagination(BaseTestGroup, ModelsFixtures):
    async def test_pages_are_newest_first(
        self, sample_user, order_factory, auth_headers, fastapi_client
    ):
        ids = [
            (await order_factory.create(user_id=sample_user.id)).id for _ in range(3)
        ]

        first = (
            await fastapi_client.get("/api/orders/?limit=2", headers=auth_headers)
        ).json()
        second = (
            await fastapi_client.get(
                "/api/orders/?limit=2&offset=2", headers=auth_headers
            )
        ).json()

        assert [o["id"] for o in first + second] == list(reversed(ids))

    @pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
    async def test_invalid_paging_is_422(self, query, auth_headers, fastapi_client):
        response = await fastapi_client.get(
            f"/api/orders/?{query}", headers=auth_headers
        )

        assert response.status_code == 422


class TestOrdersConcurrency(BaseTestGroup, ModelsFixtures):
    async def test_parallel_orders_do_not_oversell_last_item(
        self, user_factory, product_factory, fastapi_client
    ):
        product = await product_factory.create(stock=1)
        headers = []
        for _ in range(2):
            user = await user_factory.create()
            await self.container.cart_service().add_item(
                AddCartItemCmd(user_id=user.id, product_id=product.id, quantity=1)
            )
            token = await self.container.token_service().create_token(user.id)
            headers.append({"Authorization": f"Bearer {token}"})

        responses = await asyncio.gather(
            *(fastapi_client.post("/api/orders/", headers=h) for h in headers)
        )

        assert sorted(r.status_code for r in responses) == [201, 409]
        current = await self.container.product_service().get_by_id(product.id)
        assert current.stock == 0

    async def test_order_rereads_stock_after_concurrent_sale_commits(
        self, sample_user, sample_product
    ):
        await self.container.cart_service().add_item(
            AddCartItemCmd(
                user_id=sample_user.id, product_id=sample_product.id, quantity=1
            )
        )
        repo = self.container.order_repo()

        # «Другой покупатель» забирает остаток и держит строку до коммита
        async with self.container.database().transaction() as session:
            await session.execute(
                update(ProductRow)
                .where(ProductRow.id == sample_product.id)
                .values(stock=0)
            )
            task = asyncio.create_task(repo.create_from_cart(sample_user.id))
            await asyncio.sleep(0.3)

        # без FOR UPDATE заказ прочитал бы устаревший остаток и продал его снова
        with pytest.raises(InsufficientStockException):
            await asyncio.wait_for(task, timeout=5)

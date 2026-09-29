from typing import List

from src.orders.models import (
    ALLOWED_TRANSITIONS,
    Order,
    CreateOrderCmd,
    OrderStatus,
)
from src.orders.ports import OrderRepository
from src.shared.exceptions import NotFoundException
from src.shared.pagination import Pagination


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def get_by_id(self, order_id: int) -> Order:
        return await self.repo.get_by_id(order_id)

    async def get_visible(self, order_id: int, user_id: int, is_admin: bool) -> Order:
        order = await self.repo.get_by_id(order_id)
        if not is_admin and order.user_id != user_id:
            # чужой заказ неотличим от несуществующего
            raise NotFoundException(f"Order[id={order_id}]")
        return order

    async def list_by_user(
        self, user_id: int, page: Pagination | None = None
    ) -> List[Order]:
        return await self.repo.list(user_id, page=page)

    async def create(self, cmd: CreateOrderCmd) -> Order:
        order = Order(
            id=0,
            user_id=cmd.user_id,
            items=cmd.items,
            total_price=cmd.total_price,
        )
        return await self.repo.create(order)

    async def create_from_cart(self, user_id: int) -> Order:
        return await self.repo.create_from_cart(user_id)

    async def update(self, order: Order) -> Order:
        return await self.repo.update(order)

    async def change_status(self, order_id: int, new_status: OrderStatus) -> Order:
        allowed_from = {
            status
            for status, targets in ALLOWED_TRANSITIONS.items()
            if new_status in targets
        }
        return await self.repo.set_status(
            order_id,
            new_status,
            allowed_from=allowed_from,
            restore_stock=new_status == OrderStatus.CANCELLED,
        )

    async def cancel_by_owner(self, order_id: int, user_id: int) -> Order:
        await self.get_visible(order_id, user_id, is_admin=False)
        # статус проверяется в репозитории под блокировкой строки заказа
        return await self.repo.set_status(
            order_id,
            OrderStatus.CANCELLED,
            allowed_from={OrderStatus.NEW},
            restore_stock=True,
        )

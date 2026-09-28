from typing import List

from src.orders.models import Order, CreateOrderCmd, OrderStatus
from src.orders.services import OrderService
from src.shared.logger import logger
from src.shared.pagination import Pagination


class CreateOrder:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, cmd: CreateOrderCmd) -> Order:
        return self.service.create(cmd)


class CreateOrderFromCart:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, user_id: int) -> Order:
        order = self.service.create_from_cart(user_id)
        logger.info(
            "Order created from cart",
            extra={
                "order_id": order.id,
                "user_id": user_id,
                "total_price": str(order.total_price),
            },
        )
        return order


class GetOrderById:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(
        self, order_id: int, user_id: int, is_admin: bool = False
    ) -> Order:
        return self.service.get_visible(order_id, user_id, is_admin)


class ListOrdersByUser:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(
        self, user_id: int, page: Pagination | None = None
    ) -> List[Order]:
        return self.service.list_by_user(user_id, page=page)


class UpdateOrderStatus:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, order_id: int, status: OrderStatus) -> Order:
        order = self.service.change_status(order_id, status)
        logger.info(
            "Order status changed",
            extra={"order_id": order_id, "status": order.status.value},
        )
        return order


class CancelOrder:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, order_id: int, user_id: int) -> Order:
        order = self.service.cancel_by_owner(order_id, user_id)
        logger.info(
            "Order cancelled by owner", extra={"order_id": order_id, "user_id": user_id}
        )
        return order

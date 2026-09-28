from typing import List

from src.orders.models import Order, CreateOrderCmd, OrderStatus
from src.orders.services import OrderService


class CreateOrder:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, cmd: CreateOrderCmd) -> Order:
        return self.service.create(cmd)


class CreateOrderFromCart:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, user_id: int) -> Order:
        return self.service.create_from_cart(user_id)


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

    async def __call__(self, user_id: int) -> List[Order]:
        return self.service.list_by_user(user_id)


class UpdateOrderStatus:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, order_id: int, status: OrderStatus) -> Order:
        return self.service.change_status(order_id, status)


class CancelOrder:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, order_id: int, user_id: int) -> Order:
        return self.service.cancel_by_owner(order_id, user_id)

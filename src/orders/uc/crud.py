from typing import List

from src.orders.models import Order, CreateOrderCmd
from src.orders.services import OrderService


class CreateOrder:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, cmd: CreateOrderCmd) -> Order:
        return self.service.create(cmd)


class GetOrderById:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, order_id: int) -> Order:
        return self.service.get_by_id(order_id)


class ListOrdersByUser:
    def __init__(self, service: OrderService):
        self.service = service

    async def __call__(self, user_id: int) -> List[Order]:
        return self.service.list_by_user(user_id)

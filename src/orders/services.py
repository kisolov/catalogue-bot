from typing import List
from src.orders.models import Order, CreateOrderCmd
from src.orders.ports import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def get_by_id(self, order_id: int) -> Order:
        return self.repo.get_by_id(order_id)

    def list_by_user(self, user_id: int) -> List[Order]:
        return self.repo.list(user_id)

    def create(self, cmd: CreateOrderCmd) -> Order:
        order = Order(
            user_id=cmd.user_id,
            items=cmd.items,
            total_price=cmd.total_price,
        )
        return self.repo.create(order)

    def update(self, order: Order) -> Order:
        return self.repo.update(order)

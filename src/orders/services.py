from typing import List

from src.orders.models import (
    ALLOWED_TRANSITIONS,
    Order,
    CreateOrderCmd,
    OrderStatus,
)
from src.orders.ports import OrderRepository
from src.shared.exceptions import InvalidOrderTransitionException, NotFoundException


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def get_by_id(self, order_id: int) -> Order:
        return self.repo.get_by_id(order_id)

    def get_visible(self, order_id: int, user_id: int, is_admin: bool) -> Order:
        order = self.repo.get_by_id(order_id)
        if not is_admin and order.user_id != user_id:
            # чужой заказ неотличим от несуществующего
            raise NotFoundException(f"Order[id={order_id}]")
        return order

    def list_by_user(self, user_id: int) -> List[Order]:
        return self.repo.list(user_id)

    def create(self, cmd: CreateOrderCmd) -> Order:
        order = Order(
            id=0,
            user_id=cmd.user_id,
            items=cmd.items,
            total_price=cmd.total_price,
        )
        return self.repo.create(order)

    def create_from_cart(self, user_id: int) -> Order:
        return self.repo.create_from_cart(user_id)

    def update(self, order: Order) -> Order:
        return self.repo.update(order)

    def change_status(self, order_id: int, new_status: OrderStatus) -> Order:
        order = self.repo.get_by_id(order_id)
        if new_status not in ALLOWED_TRANSITIONS[order.status]:
            raise InvalidOrderTransitionException(
                order.status.value, new_status.value
            )
        return self.repo.set_status(
            order_id, new_status, restore_stock=new_status == OrderStatus.CANCELLED
        )

    def cancel_by_owner(self, order_id: int, user_id: int) -> Order:
        order = self.get_visible(order_id, user_id, is_admin=False)
        if order.status != OrderStatus.NEW:
            raise InvalidOrderTransitionException(
                order.status.value, OrderStatus.CANCELLED.value
            )
        return self.repo.set_status(order_id, OrderStatus.CANCELLED, True)

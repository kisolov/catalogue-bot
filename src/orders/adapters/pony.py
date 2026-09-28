from typing import List

from pony.orm import db_session, commit

from src.orders.models import Order
from src.orders.ports import OrderRepository
from src.shared.orm.models import PonyOrder, PonyOrderItem
from src.shared.exceptions import NotFoundException, UniqueViolationException


class PonyOrderRepository(OrderRepository):
    @db_session
    def get_by_id(self, order_id: int) -> Order:
        order = PonyOrder.get(id=order_id)
        if not order:
            raise NotFoundException(f"Order[id={order_id}]")
        return Order.model_validate(order)

    @db_session
    def list(self, user_id: int) -> List[Order]:
        orders = PonyOrder.select(lambda o: o.user.id == user_id).prefetch(
            PonyOrderItem
        )
        return [Order.model_validate(o) for o in orders]

    @db_session
    def create(self, order: Order) -> Order:
        try:
            pony_order = PonyOrder(
                user=order.user_id,
                status=order.status.value,
                total_price=order.total_price,
            )
            commit()

            for item in order.items:
                PonyOrderItem(
                    order=pony_order,
                    product=item.product_id,
                    product_name=item.product_name,
                    price=item.price,
                    quantity=item.quantity,
                )
            commit()
        except Exception as e:
            raise UniqueViolationException(f"Order creation failed: {str(e)}")

        return Order.model_validate(pony_order)

    @db_session
    def update(self, order: Order) -> Order:
        pony_order = PonyOrder.get(id=order.id)
        if not pony_order:
            raise NotFoundException(f"Order[id={order.id}]")

        pony_order.status = order.status.value
        pony_order.total_price = order.total_price

        existing_items_map = {item.product_id: item for item in pony_order.items}
        incoming_items_map = {item.product_id: item for item in order.items}

        for product_id, item_to_delete in existing_items_map.items():
            if product_id not in incoming_items_map:
                item_to_delete.delete()

        for product_id, incoming_item in incoming_items_map.items():
            if product_id in existing_items_map:
                existing_item = existing_items_map[product_id]
                existing_item.price = incoming_item.price
                existing_item.quantity = incoming_item.quantity
                existing_item.product_name = incoming_item.product_name
            else:
                PonyOrderItem(
                    order=pony_order,
                    product=incoming_item.product_id,
                    product_name=incoming_item.product_name,
                    price=incoming_item.price,
                    quantity=incoming_item.quantity,
                )

        return Order.model_validate(pony_order)

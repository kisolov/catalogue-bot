from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from pony.orm import db_session, select, flush, desc

from src.orders.models import Order, OrderItem, OrderStatus
from src.orders.ports import OrderRepository
from src.shared.orm.models import (
    PonyCartItem,
    PonyOrder,
    PonyOrderItem,
    PonyProduct,
)
from src.shared.exceptions import (
    EmptyCartException,
    InsufficientStockException,
    NotFoundException,
    ProductUnavailableException,
)


class PonyOrderRepository(OrderRepository):
    @staticmethod
    def _to_domain(pony_order: PonyOrder) -> Order:
        return Order(
            id=pony_order.id,
            user_id=pony_order.user.id if pony_order.user else None,
            status=OrderStatus(pony_order.status),
            total_price=pony_order.total_price,
            items=[
                OrderItem(
                    id=item.id,
                    order_id=pony_order.id,
                    product_id=item.product.id,
                    product_name=item.product_name,
                    price=item.price,
                    quantity=item.quantity,
                )
                for item in pony_order.items.order_by(PonyOrderItem.id)
            ],
            created_at=pony_order.created_at,
            updated_at=pony_order.updated_at,
        )

    @db_session
    def get_by_id(self, order_id: int) -> Order:
        order = PonyOrder.get(id=order_id)
        if not order:
            raise NotFoundException(f"Order[id={order_id}]")
        return self._to_domain(order)

    @db_session
    def list(self, user_id: int) -> List[Order]:
        orders = select(o for o in PonyOrder if o.user.id == user_id).order_by(
            desc(PonyOrder.id)
        )
        return [self._to_domain(o) for o in orders]

    @db_session
    def create(self, order: Order) -> Order:
        now = datetime.now(timezone.utc)
        pony_order = PonyOrder(
            user=order.user_id,
            status=order.status.value,
            total_price=order.total_price,
            created_at=now,
            updated_at=now,
        )
        flush()
        for item in order.items:
            PonyOrderItem(
                order=pony_order,
                product=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
            )
        flush()
        return self._to_domain(pony_order)

    @db_session
    def create_from_cart(self, user_id: int) -> Order:
        cart_items = list(
            select(i for i in PonyCartItem if i.user.id == user_id).order_by(
                PonyCartItem.id
            )
        )
        if not cart_items:
            raise EmptyCartException()

        now = datetime.now(timezone.utc)
        lines = []
        total = Decimal("0")
        for cart_item in cart_items:
            # блокировка строки товара: параллельные заказы не продадут остаток дважды
            product = PonyProduct.get_for_update(id=cart_item.product.id)
            if not product.is_active:
                raise ProductUnavailableException(product.id)
            if product.stock < cart_item.quantity:
                raise InsufficientStockException(product.id)
            lines.append((cart_item, product))
            total += product.price * cart_item.quantity

        pony_order = PonyOrder(
            user=user_id,
            status=OrderStatus.NEW.value,
            total_price=total,
            created_at=now,
            updated_at=now,
        )
        flush()
        for cart_item, product in lines:
            PonyOrderItem(
                order=pony_order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
            )
            product.stock -= cart_item.quantity
            product.updated_at = now
            cart_item.delete()
        flush()
        return self._to_domain(pony_order)

    @db_session
    def set_status(
        self, order_id: int, status: OrderStatus, restore_stock: bool
    ) -> Order:
        pony_order = PonyOrder.get_for_update(id=order_id)
        if not pony_order:
            raise NotFoundException(f"Order[id={order_id}]")

        if restore_stock:
            for item in pony_order.items:
                product = PonyProduct.get_for_update(id=item.product.id)
                product.stock += item.quantity

        pony_order.status = status.value
        pony_order.updated_at = datetime.now(timezone.utc)
        flush()
        return self._to_domain(pony_order)

    @db_session
    def update(self, order: Order) -> Order:
        pony_order = PonyOrder.get(id=order.id)
        if not pony_order:
            raise NotFoundException(f"Order[id={order.id}]")

        pony_order.status = order.status.value
        pony_order.total_price = order.total_price
        pony_order.updated_at = datetime.now(timezone.utc)

        existing = {item.product.id: item for item in pony_order.items}
        incoming = {item.product_id: item for item in order.items}

        for product_id, item in existing.items():
            if product_id not in incoming:
                item.delete()

        for product_id, new_item in incoming.items():
            if product_id in existing:
                current = existing[product_id]
                current.price = new_item.price
                current.quantity = new_item.quantity
                current.product_name = new_item.product_name
            else:
                PonyOrderItem(
                    order=pony_order,
                    product=product_id,
                    product_name=new_item.product_name,
                    price=new_item.price,
                    quantity=new_item.quantity,
                )
        flush()
        return self._to_domain(pony_order)

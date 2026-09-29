from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.orders.models import Order, OrderItem, OrderStatus
from src.orders.ports import OrderRepository
from src.shared.db import Database
from src.shared.exceptions import (
    EmptyCartException,
    InsufficientStockException,
    InvalidOrderTransitionException,
    NotFoundException,
    ProductUnavailableException,
)
from src.shared.orm.models import CartItemRow, OrderItemRow, OrderRow, ProductRow
from src.shared.pagination import Pagination


class PostgresOrderRepository(OrderRepository):
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    async def _with_items(session: AsyncSession, rows: list[OrderRow]) -> list[Order]:
        items_by_order: dict[int, list[OrderItemRow]] = {}
        if rows:
            found = await session.scalars(
                select(OrderItemRow)
                .where(OrderItemRow.order_id.in_([row.id for row in rows]))
                .order_by(OrderItemRow.id)
            )
            for item in found:
                items_by_order.setdefault(item.order_id, []).append(item)
        return [
            Order(
                id=row.id,
                user_id=row.user_id,
                status=OrderStatus(row.status),
                total_price=row.total_price,
                items=[
                    OrderItem(
                        id=item.id,
                        order_id=row.id,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        price=item.price,
                        quantity=item.quantity,
                    )
                    for item in items_by_order.get(row.id, [])
                ],
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    @classmethod
    async def _one(cls, session: AsyncSession, row: OrderRow) -> Order:
        return (await cls._with_items(session, [row]))[0]

    async def get_by_id(self, order_id: int) -> Order:
        async with self.db.transaction() as session:
            order = await session.get(OrderRow, order_id)
            if order is None:
                raise NotFoundException(f"Order[id={order_id}]")
            return await self._one(session, order)

    async def list(self, user_id: int, page: Pagination | None = None) -> List[Order]:
        async with self.db.transaction() as session:
            query = (
                select(OrderRow)
                .where(OrderRow.user_id == user_id)
                .order_by(OrderRow.id.desc())
            )
            if page:
                query = query.limit(page.limit).offset(page.offset)
            rows = list(await session.scalars(query))
            return await self._with_items(session, rows)

    async def create(self, order: Order) -> Order:
        async with self.db.transaction() as session:
            now = datetime.now(timezone.utc)
            row = OrderRow(
                user_id=order.user_id,
                status=order.status.value,
                total_price=order.total_price,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            await session.flush()
            session.add_all(
                OrderItemRow(
                    order_id=row.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    price=item.price,
                    quantity=item.quantity,
                )
                for item in order.items
            )
            await session.flush()
            return await self._one(session, row)

    async def create_from_cart(self, user_id: int) -> Order:
        async with self.db.transaction() as session:
            cart_items = list(
                await session.scalars(
                    select(CartItemRow)
                    .where(CartItemRow.user_id == user_id)
                    .order_by(CartItemRow.id)
                )
            )
            if not cart_items:
                raise EmptyCartException()

            now = datetime.now(timezone.utc)
            products = await self._lock_products(
                session, [item.product_id for item in cart_items]
            )
            lines: list[tuple[CartItemRow, ProductRow]] = []
            total = Decimal("0")
            for cart_item in cart_items:
                product = products.get(cart_item.product_id)
                if product is None or not product.is_active:
                    raise ProductUnavailableException(cart_item.product_id)
                if product.stock < cart_item.quantity:
                    raise InsufficientStockException(product.id)
                lines.append((cart_item, product))
                total += product.price * cart_item.quantity

            row = OrderRow(
                user_id=user_id,
                status=OrderStatus.NEW.value,
                total_price=total,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            await session.flush()
            for cart_item, product in lines:
                session.add(
                    OrderItemRow(
                        order_id=row.id,
                        product_id=product.id,
                        product_name=product.name,
                        price=product.price,
                        quantity=cart_item.quantity,
                    )
                )
                product.stock -= cart_item.quantity
                product.updated_at = now
                await session.delete(cart_item)
            await session.flush()
            return await self._one(session, row)

    @staticmethod
    async def _lock_products(
        session: AsyncSession, product_ids: List[int]
    ) -> dict[int, ProductRow]:
        # блокировка строк: параллельные заказы не продадут остаток дважды;
        # единый порядок по id исключает deadlock встречных заказов
        rows = await session.scalars(
            select(ProductRow)
            .where(ProductRow.id.in_(product_ids))
            .order_by(ProductRow.id)
            .with_for_update()
        )
        return {row.id: row for row in rows}

    async def set_status(
        self,
        order_id: int,
        status: OrderStatus,
        allowed_from: set[OrderStatus],
        restore_stock: bool,
    ) -> Order:
        async with self.db.transaction() as session:
            row = await session.scalar(
                select(OrderRow).where(OrderRow.id == order_id).with_for_update()
            )
            if row is None:
                raise NotFoundException(f"Order[id={order_id}]")
            # проверка под блокировкой: параллельная смена статуса уже видна
            current = OrderStatus(row.status)
            if current not in allowed_from:
                raise InvalidOrderTransitionException(current.value, status.value)

            if restore_stock:
                items = list(
                    await session.scalars(
                        select(OrderItemRow).where(OrderItemRow.order_id == order_id)
                    )
                )
                products = await self._lock_products(
                    session, [item.product_id for item in items]
                )
                for item in items:
                    products[item.product_id].stock += item.quantity

            row.status = status.value
            row.updated_at = datetime.now(timezone.utc)
            await session.flush()
            return await self._one(session, row)

    async def update(self, order: Order) -> Order:
        async with self.db.transaction() as session:
            row = await session.get(OrderRow, order.id)
            if row is None:
                raise NotFoundException(f"Order[id={order.id}]")

            row.status = order.status.value
            row.total_price = order.total_price
            row.updated_at = datetime.now(timezone.utc)

            existing = {
                item.product_id: item
                for item in await session.scalars(
                    select(OrderItemRow).where(OrderItemRow.order_id == order.id)
                )
            }
            incoming = {item.product_id: item for item in order.items}

            for product_id, item in existing.items():
                if product_id not in incoming:
                    await session.delete(item)

            for product_id, new_item in incoming.items():
                if product_id in existing:
                    current = existing[product_id]
                    current.price = new_item.price
                    current.quantity = new_item.quantity
                    current.product_name = new_item.product_name
                else:
                    session.add(
                        OrderItemRow(
                            order_id=order.id,
                            product_id=product_id,
                            product_name=new_item.product_name,
                            price=new_item.price,
                            quantity=new_item.quantity,
                        )
                    )
            await session.flush()
            return await self._one(session, row)

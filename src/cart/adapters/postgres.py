from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.cart.models import (
    MAX_QUANTITY,
    CartItem,
    RemoveCartItemCmd,
    Cart,
    AddCartItemCmd,
)
from src.cart.ports import CartRepository
from src.shared.db import Database
from src.shared.exceptions import (
    InvalidCartQuantityException,
    NotFoundException,
    UniqueViolationException,
)
from src.shared.orm.models import CartItemRow, ProductRow, UserRow


class PostgresCartRepository(CartRepository):
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _to_domain(row: CartItemRow) -> CartItem:
        return CartItem(
            id=row.id,
            user_id=row.user_id,
            product_id=row.product_id,
            quantity=row.quantity,
            added_at=row.added_at,
        )

    async def get_cart(self, user_id: int) -> Cart:
        async with self.db.transaction() as session:
            items = await session.scalars(
                select(CartItemRow)
                .where(CartItemRow.user_id == user_id)
                .order_by(CartItemRow.id)
            )
            return Cart(user_id=user_id, items=[self._to_domain(i) for i in items])

    async def add_item(self, cmd: AddCartItemCmd) -> CartItem:
        async with self.db.transaction() as session:
            if not await session.get(UserRow, cmd.user_id):
                raise NotFoundException(f"User[id={cmd.user_id}]")
            if not await session.get(ProductRow, cmd.product_id):
                raise NotFoundException(f"Product[id={cmd.product_id}]")

            now = datetime.now(timezone.utc)
            # блокировка строки: параллельные добавления не потеряют приращение
            item = await session.scalar(
                select(CartItemRow)
                .where(
                    CartItemRow.user_id == cmd.user_id,
                    CartItemRow.product_id == cmd.product_id,
                )
                .with_for_update()
            )

            if item:
                if item.quantity + cmd.quantity > MAX_QUANTITY:
                    raise InvalidCartQuantityException(cmd.product_id, MAX_QUANTITY)
                item.quantity += cmd.quantity
                item.updated_at = now
            else:
                item = CartItemRow(
                    user_id=cmd.user_id,
                    product_id=cmd.product_id,
                    quantity=cmd.quantity,
                    added_at=now,
                    updated_at=now,
                )
                session.add(item)
            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException(
                    f"CartItem[user_id={cmd.user_id}, product_id={cmd.product_id}]"
                )
            return self._to_domain(item)

    async def remove_item(self, cmd: RemoveCartItemCmd) -> None:
        async with self.db.transaction() as session:
            result = await session.execute(
                delete(CartItemRow).where(
                    CartItemRow.user_id == cmd.user_id,
                    CartItemRow.product_id == cmd.product_id,
                )
            )
            if result.rowcount == 0:
                raise NotFoundException(
                    f"CartItem[user_id={cmd.user_id}, product_id={cmd.product_id}]"
                )

    async def clear(self, user_id: int) -> None:
        async with self.db.transaction() as session:
            await session.execute(
                delete(CartItemRow).where(CartItemRow.user_id == user_id)
            )

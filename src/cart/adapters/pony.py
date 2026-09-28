from datetime import datetime, timezone

from pony.orm import db_session, select, TransactionIntegrityError

from src.cart.models import CartItem, RemoveCartItemCmd, Cart, AddCartItemCmd
from src.cart.ports import CartRepository
from src.shared.exceptions import NotFoundException, UniqueViolationException
from src.shared.orm.models import PonyCartItem, PonyUser, PonyProduct, db


class PonyCartRepository(CartRepository):
    @db_session
    def get_cart(self, user_id: int) -> Cart:
        items = select(i for i in PonyCartItem if i.user.id == user_id)

        return Cart(
            user_id=user_id,
            items=[
                CartItem(
                    id=i.id,
                    user_id=i.user.id,
                    product_id=i.product.id,
                    quantity=i.quantity,
                    added_at=i.added_at,
                )
                for i in items
            ],
        )

    @db_session
    def add_item(self, cmd: AddCartItemCmd) -> CartItem:
        user = PonyUser.get(id=cmd.user_id)
        if not user:
            raise NotFoundException(f"User[id={cmd.user_id}]")

        product = PonyProduct.get(id=cmd.product_id)
        if not product:
            raise NotFoundException(f"Product[id={cmd.product_id}]")

        now = datetime.now(timezone.utc)

        item = PonyCartItem.get(user=user, product=product)

        if item:
            item.quantity += cmd.quantity
            item.updated_at = now
        else:
            try:
                item = PonyCartItem(
                    user=user,
                    product=product,
                    quantity=cmd.quantity,
                    added_at=now,
                    updated_at=now,
                )
                # Flush to get the ID
                db.flush()
            except TransactionIntegrityError:
                raise UniqueViolationException(
                    f"CartItem[user_id={cmd.user_id}, product_id={cmd.product_id}]"
                )

        return CartItem(
            id=item.id,
            user_id=item.user.id,
            product_id=item.product.id,
            quantity=item.quantity,
            added_at=item.added_at,
        )

    @db_session
    def remove_item(self, cmd: RemoveCartItemCmd) -> None:
        item = PonyCartItem.get(
            lambda i: i.user.id == cmd.user_id and i.product.id == cmd.product_id
        )
        if not item:
            raise NotFoundException(
                f"CartItem[user_id={cmd.user_id}, product_id={cmd.product_id}]"
            )
        item.delete()

    @db_session
    def clear(self, user_id: int) -> None:
        items = select(i for i in PonyCartItem if i.user.id == user_id)
        for item in items:
            item.delete()

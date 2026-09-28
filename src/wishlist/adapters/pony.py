from datetime import datetime, timezone

from pony.orm import db_session, select, TransactionIntegrityError, flush

from src.wishlist.models import (
    Favorite,
    Wishlist,
    AddInWishlistCmd,
    RemoveFromWishlistCmd,
)
from src.wishlist.ports import WishlistRepository
from src.shared.orm.models import PonyFavorite
from src.shared.exceptions import NotFoundException, UniqueViolationException


class PonyWishlistRepository(WishlistRepository):
    @db_session
    def to_domain(self, pony: PonyFavorite) -> Favorite:
        return Favorite(
            id=pony.id,
            user_id=pony.user.id,
            product_id=pony.product.id,
            added_at=pony.added_at,
        )

    @db_session
    def add(self, cmd: AddInWishlistCmd) -> Favorite:
        if PonyFavorite.get(user=cmd.user_id, product=cmd.product_id):
            raise UniqueViolationException(
                f"Favorite[user_id={cmd.user_id}, product_id={cmd.product_id}]"
            )
        try:
            created = PonyFavorite(
                user=cmd.user_id,
                product=cmd.product_id,
                added_at=datetime.now(timezone.utc),
            )
            flush()
            return self.to_domain(created)
        except TransactionIntegrityError:
            raise UniqueViolationException(
                f"Favorite[user_id={cmd.user_id}, product_id={cmd.product_id}]"
            )

    @db_session
    def remove(self, cmd: RemoveFromWishlistCmd) -> None:
        fav = PonyFavorite.get(user=cmd.user_id, product=cmd.product_id)
        if not fav:
            raise NotFoundException(
                f"Favorite[user_id={cmd.user_id}, product_id={cmd.product_id}]"
            )
        fav.delete()

    @db_session
    def get(self, user_id: int) -> Wishlist:
        favorites = select(f for f in PonyFavorite if f.user.id == user_id)[:]

        product_favorites = [self.to_domain(f) for f in favorites]

        return Wishlist(
            user_id=user_id,
            products=product_favorites,
        )

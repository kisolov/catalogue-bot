from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from src.shared.db import Database
from src.shared.exceptions import NotFoundException, UniqueViolationException
from src.shared.orm.models import FavoriteRow, ProductRow
from src.wishlist.models import (
    Favorite,
    Wishlist,
    AddInWishlistCmd,
    RemoveFromWishlistCmd,
)
from src.wishlist.ports import WishlistRepository


class PostgresWishlistRepository(WishlistRepository):
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _to_domain(row: FavoriteRow) -> Favorite:
        return Favorite(
            id=row.id,
            user_id=row.user_id,
            product_id=row.product_id,
            added_at=row.added_at,
        )

    async def add(self, cmd: AddInWishlistCmd) -> Favorite:
        async with self.db.transaction() as session:
            if not await session.get(ProductRow, cmd.product_id):
                raise NotFoundException(f"Product[id={cmd.product_id}]")
            duplicate = await session.scalar(
                select(FavoriteRow.id).where(
                    FavoriteRow.user_id == cmd.user_id,
                    FavoriteRow.product_id == cmd.product_id,
                )
            )
            if duplicate:
                raise UniqueViolationException(
                    f"Favorite[user_id={cmd.user_id}, product_id={cmd.product_id}]"
                )
            favorite = FavoriteRow(
                user_id=cmd.user_id,
                product_id=cmd.product_id,
                added_at=datetime.now(timezone.utc),
            )
            session.add(favorite)
            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException(
                    f"Favorite[user_id={cmd.user_id}, product_id={cmd.product_id}]"
                )
            return self._to_domain(favorite)

    async def remove(self, cmd: RemoveFromWishlistCmd) -> None:
        async with self.db.transaction() as session:
            result = await session.execute(
                delete(FavoriteRow).where(
                    FavoriteRow.user_id == cmd.user_id,
                    FavoriteRow.product_id == cmd.product_id,
                )
            )
            if result.rowcount == 0:
                raise NotFoundException(
                    f"Favorite[user_id={cmd.user_id}, product_id={cmd.product_id}]"
                )

    async def get(self, user_id: int) -> Wishlist:
        async with self.db.transaction() as session:
            favorites = await session.scalars(
                select(FavoriteRow)
                .where(FavoriteRow.user_id == user_id)
                .order_by(FavoriteRow.id)
            )
            return Wishlist(
                user_id=user_id,
                products=[self._to_domain(f) for f in favorites],
            )

from src.wishlist.models import (
    Favorite,
    Wishlist,
    AddInWishlistCmd,
    RemoveFromWishlistCmd,
)
from src.wishlist.ports import WishlistRepository


class WishlistService:
    def __init__(self, repo: WishlistRepository):
        self.repo = repo

    async def add(self, cmd: AddInWishlistCmd) -> Favorite:
        return await self.repo.add(cmd)

    async def remove(self, cmd: RemoveFromWishlistCmd) -> None:
        await self.repo.remove(cmd)

    async def get(self, user_id) -> Wishlist:
        return await self.repo.get(user_id)

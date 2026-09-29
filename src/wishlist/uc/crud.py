from src.wishlist.models import (
    Favorite,
    Wishlist,
    AddInWishlistCmd,
    RemoveFromWishlistCmd,
)
from src.wishlist.services import WishlistService


class AddInWishlist:
    def __init__(self, service: WishlistService):
        self.service = service

    async def __call__(self, cmd: AddInWishlistCmd) -> Favorite:
        return await self.service.add(cmd)


class RemoveFromWishlist:
    def __init__(self, service: WishlistService):
        self.service = service

    async def __call__(self, cmd: RemoveFromWishlistCmd) -> None:
        return await self.service.remove(cmd)


class GetWishlist:
    def __init__(self, service: WishlistService):
        self.service = service

    async def __call__(self, user_id: int) -> Wishlist:
        return await self.service.get(user_id)

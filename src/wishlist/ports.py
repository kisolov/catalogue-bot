from abc import ABC, abstractmethod

from src.wishlist.models import (
    Favorite,
    Wishlist,
    AddInWishlistCmd,
    RemoveFromWishlistCmd,
)


class WishlistRepository(ABC):
    @abstractmethod
    async def add(self, cmd: AddInWishlistCmd) -> Favorite: ...

    @abstractmethod
    async def remove(self, cmd: RemoveFromWishlistCmd) -> None: ...

    @abstractmethod
    async def get(self, user_id: int) -> Wishlist: ...

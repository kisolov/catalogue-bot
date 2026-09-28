from abc import ABC, abstractmethod

from src.wishlist.models import (
    Favorite,
    Wishlist,
    AddInWishlistCmd,
    RemoveFromWishlistCmd,
)


class WishlistRepository(ABC):
    @abstractmethod
    def add(self, cmd: AddInWishlistCmd) -> Favorite: ...

    @abstractmethod
    def remove(self, cmd: RemoveFromWishlistCmd) -> None: ...

    @abstractmethod
    def get(self, user_id: int) -> Wishlist: ...

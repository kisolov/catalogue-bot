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

    def add(self, cmd: AddInWishlistCmd) -> Favorite:
        return self.repo.add(cmd)

    def remove(self, cmd: RemoveFromWishlistCmd) -> None:
        self.repo.remove(cmd)

    def get(self, user_id) -> Wishlist:
        return self.repo.get(user_id)

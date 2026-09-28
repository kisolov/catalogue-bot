from src.cart.models import Cart, CartItem, AddCartItemCmd, RemoveCartItemCmd
from src.cart.ports import CartRepository


class CartService:
    def __init__(self, repo: CartRepository):
        self.repo = repo

    def get_by_user_id(self, user_id: int) -> Cart:
        return self.repo.get_cart(user_id)

    def add_item(self, cmd: AddCartItemCmd) -> CartItem:
        return self.repo.add_item(cmd)

    def remove_item(self, cmd: RemoveCartItemCmd) -> None:
        self.repo.remove_item(cmd)

    def clear(self, user_id: int) -> None:
        self.repo.clear(user_id)

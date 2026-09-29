from src.cart.models import Cart, CartItem, AddCartItemCmd, RemoveCartItemCmd
from src.cart.ports import CartRepository


class CartService:
    def __init__(self, repo: CartRepository):
        self.repo = repo

    async def get_by_user_id(self, user_id: int) -> Cart:
        return await self.repo.get_cart(user_id)

    async def add_item(self, cmd: AddCartItemCmd) -> CartItem:
        return await self.repo.add_item(cmd)

    async def remove_item(self, cmd: RemoveCartItemCmd) -> None:
        await self.repo.remove_item(cmd)

    async def clear(self, user_id: int) -> None:
        await self.repo.clear(user_id)

from src.cart.models import RemoveCartItemCmd, AddCartItemCmd, Cart, CartItem
from src.cart.services import CartService


class GetCart:
    def __init__(self, service: CartService):
        self.service = service

    async def __call__(self, user_id: int) -> Cart:
        return self.service.get_by_user_id(user_id)


class AddToCart:
    def __init__(self, service: CartService):
        self.service = service

    async def __call__(self, cmd: AddCartItemCmd) -> CartItem:
        return self.service.add_item(cmd)


class RemoveFromCart:
    def __init__(self, service: CartService):
        self.service = service

    async def __call__(self, cmd: RemoveCartItemCmd) -> None:
        self.service.remove_item(cmd)


class ClearCart:
    def __init__(self, service: CartService):
        self.service = service

    async def __call__(self, user_id: int) -> None:
        self.service.clear(user_id)

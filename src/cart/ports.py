from abc import ABC, abstractmethod

from src.cart.models import CartItem, AddCartItemCmd, RemoveCartItemCmd, Cart


class CartRepository(ABC):
    @abstractmethod
    async def get_cart(self, user_id: int) -> Cart: ...

    @abstractmethod
    async def add_item(self, cmd: AddCartItemCmd) -> CartItem: ...

    @abstractmethod
    async def remove_item(self, cmd: RemoveCartItemCmd) -> None: ...

    @abstractmethod
    async def clear(self, user_id: int) -> None: ...

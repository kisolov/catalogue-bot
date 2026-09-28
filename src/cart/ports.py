from abc import ABC, abstractmethod

from src.cart.models import CartItem, AddCartItemCmd, RemoveCartItemCmd, Cart


class CartRepository(ABC):
    @abstractmethod
    def get_cart(self, user_id: int) -> Cart: ...

    @abstractmethod
    def add_item(self, cmd: AddCartItemCmd) -> CartItem: ...

    @abstractmethod
    def remove_item(self, cmd: RemoveCartItemCmd) -> None: ...

    @abstractmethod
    def clear(self, user_id: int) -> None: ...

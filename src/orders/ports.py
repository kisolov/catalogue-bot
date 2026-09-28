from abc import ABC, abstractmethod
from typing import List, Optional

from src.orders.models import Order, OrderStatus
from src.shared.pagination import Pagination


class OrderRepository(ABC):

    @abstractmethod
    def get_by_id(self, order_id: int) -> Order: ...

    @abstractmethod
    def list(self, user_id: int, page: Optional[Pagination] = None) -> List[Order]: ...

    @abstractmethod
    def create(self, order: Order) -> Order: ...

    @abstractmethod
    def update(self, order: Order) -> Order: ...

    @abstractmethod
    def create_from_cart(self, user_id: int) -> Order:
        """Атомарно: заказ из корзины, списание остатков, очистка корзины."""

    @abstractmethod
    def set_status(
        self, order_id: int, status: OrderStatus, restore_stock: bool
    ) -> Order:
        """Атомарно: смена статуса и (при отмене) возврат остатков."""

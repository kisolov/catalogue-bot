from abc import ABC, abstractmethod
from typing import List

from src.orders.models import Order


class OrderRepository(ABC):

    @abstractmethod
    def get_by_id(self, order_id: int) -> Order: ...

    @abstractmethod
    def list(self, user_id: int) -> List[Order]: ...

    @abstractmethod
    def create(self, order: Order) -> Order: ...

    @abstractmethod
    def update(self, order: Order) -> Order: ...

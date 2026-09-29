from abc import ABC, abstractmethod
from typing import List, Optional

from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.shared.pagination import Pagination


class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Product: ...

    @abstractmethod
    async def list(
        self,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = True,
        page: Optional[Pagination] = None,
    ) -> List[Product]: ...

    @abstractmethod
    async def create(self, cmd: CreateProductCmd) -> Product: ...

    @abstractmethod
    async def update(self, cmd: UpdateProductCmd) -> Product: ...

    @abstractmethod
    async def delete(self, product_id: int) -> None: ...

from abc import ABC, abstractmethod
from typing import List, Optional
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.shared.pagination import Pagination


class CategoryRepository(ABC):

    @abstractmethod
    async def get_by_id(self, category_id: int) -> Category: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Category: ...

    @abstractmethod
    async def list(
        self, parent_id: Optional[int] = None, page: Optional[Pagination] = None
    ) -> List[Category]: ...

    @abstractmethod
    async def create(self, cmd: CreateCategoryCmd) -> Category: ...

    @abstractmethod
    async def update(self, cmd: UpdateCategoryCmd) -> Category: ...

    @abstractmethod
    async def delete(self, category_id: int) -> None: ...

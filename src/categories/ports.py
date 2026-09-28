from abc import ABC, abstractmethod
from typing import List, Optional
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.shared.pagination import Pagination


class CategoryRepository(ABC):

    @abstractmethod
    def get_by_id(self, category_id: int) -> Category: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Category: ...

    @abstractmethod
    def list(
        self, parent_id: Optional[int] = None, page: Optional[Pagination] = None
    ) -> List[Category]: ...

    @abstractmethod
    def create(self, cmd: CreateCategoryCmd) -> Category: ...

    @abstractmethod
    def update(self, cmd: UpdateCategoryCmd) -> Category: ...

    @abstractmethod
    def delete(self, category_id: int) -> None: ...

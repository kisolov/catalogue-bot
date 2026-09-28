from abc import ABC, abstractmethod
from typing import List, Optional
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd


class CategoryRepository(ABC):

    @abstractmethod
    def get_by_id(self, category_id: int) -> Category: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Category: ...

    @abstractmethod
    def list(self, parent_id: Optional[int] = None) -> List[Category]: ...

    @abstractmethod
    def create(self, cmd: CreateCategoryCmd) -> Category: ...

    @abstractmethod
    def update(self, cmd: UpdateCategoryCmd) -> Category: ...

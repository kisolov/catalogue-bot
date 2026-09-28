from typing import List

from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.services import CategoryService


class CreateCategory:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, cmd: CreateCategoryCmd) -> Category:
        return self.service.create(cmd)


class UpdateCategory:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, cmd: UpdateCategoryCmd) -> Category:
        return self.service.update(cmd)


class GetCategoryById:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, category_id: int) -> Category:
        return self.service.get_by_id(category_id)


class ListCategories:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self) -> List[Category]:
        return self.service.list()

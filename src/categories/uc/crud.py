from typing import List

from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.services import CategoryService
from src.shared.logger import logger
from src.shared.pagination import Pagination


class CreateCategory:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, cmd: CreateCategoryCmd) -> Category:
        category = self.service.create(cmd)
        logger.info("Category created", extra={"category_id": category.id})
        return category


class UpdateCategory:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, cmd: UpdateCategoryCmd) -> Category:
        category = self.service.update(cmd)
        logger.info("Category updated", extra={"category_id": category.id})
        return category


class GetCategoryById:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, category_id: int) -> Category:
        return self.service.get_by_id(category_id)


class ListCategories:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, page: Pagination | None = None) -> List[Category]:
        return self.service.list(page=page)


class DeleteCategory:
    def __init__(self, service: CategoryService):
        self.service = service

    async def __call__(self, category_id: int) -> None:
        self.service.delete(category_id)
        logger.info("Category deleted", extra={"category_id": category_id})

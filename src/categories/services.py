from typing import List
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.ports import CategoryRepository
from src.shared.pagination import Pagination


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def get_by_id(self, category_id: int) -> Category:
        return await self.repo.get_by_id(category_id)

    async def get_by_slug(self, slug: str) -> Category:
        return await self.repo.get_by_slug(slug)

    async def list(
        self, parent_id: int | None = None, page: Pagination | None = None
    ) -> List[Category]:
        return await self.repo.list(parent_id=parent_id, page=page)

    async def create(self, cmd: CreateCategoryCmd) -> Category:
        return await self.repo.create(cmd)

    async def update(self, cmd: UpdateCategoryCmd) -> Category:
        return await self.repo.update(cmd)

    async def delete(self, category_id: int) -> None:
        await self.repo.delete(category_id)

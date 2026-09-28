from typing import List
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.ports import CategoryRepository


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    def get_by_id(self, category_id: int) -> Category:
        return self.repo.get_by_id(category_id)

    def get_by_slug(self, slug: str) -> Category:
        return self.repo.get_by_slug(slug)

    def list(self, parent_id: int | None = None) -> List[Category]:
        return self.repo.list(parent_id=parent_id)

    def create(self, cmd: CreateCategoryCmd) -> Category:
        return self.repo.create(cmd)

    def update(self, cmd: UpdateCategoryCmd) -> Category:
        return self.repo.update(cmd)

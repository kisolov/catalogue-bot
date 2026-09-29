from typing import Optional
from faker import Faker
from src.categories.models import Category, CreateCategoryCmd
from src.categories.services import CategoryService


class CategoryFactory:
    def __init__(self, category_service: CategoryService) -> None:
        self.category_service = category_service
        self.faker = Faker()

    async def create(
        self,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> Category:
        if name is None:
            name = self.faker.unique.word().capitalize()
        if slug is None:
            slug = self.faker.unique.slug()

        cmd = CreateCategoryCmd(
            name=name,
            slug=slug,
            parent_id=parent_id,
        )
        return await self.category_service.create(cmd)

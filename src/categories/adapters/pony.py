from datetime import datetime, timezone
from pony.orm import db_session, select, TransactionIntegrityError, flush

from src.shared.exceptions import NotFoundException, UniqueViolationException
from src.shared.orm.models import PonyCategory
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.ports import CategoryRepository


class PonyCategoryRepository(CategoryRepository):

    @db_session
    def get_by_id(self, category_id: int) -> Category:
        category = PonyCategory.get(id=category_id)
        if not category:
            raise NotFoundException(f"Category[id={category_id}]")
        return Category.model_validate(category)

    @db_session
    def get_by_slug(self, slug: str) -> Category:
        category = PonyCategory.get(slug=slug)
        if not category:
            raise NotFoundException(f"Category[slug={slug}]")
        return Category.model_validate(category)

    @db_session
    def list(self, parent_id: int | None = None) -> list[Category]:
        query = select(c for c in PonyCategory)
        if parent_id is not None:
            query = query.filter(lambda c: c.parent.id == parent_id)
        categories = query[:]
        return [Category.model_validate(c) for c in categories]

    @db_session
    def create(self, cmd: CreateCategoryCmd) -> Category:
        if PonyCategory.get(slug=cmd.slug):
            raise UniqueViolationException(f"Category[slug={cmd.slug}]")
        try:
            pony_category = PonyCategory(
                name=cmd.name,
                slug=cmd.slug,
                parent=cmd.parent_id,
                created_at=datetime.now(timezone.utc),
            )
            flush()
        except TransactionIntegrityError:
            raise UniqueViolationException(f"Category[slug={cmd.slug}]")
        return Category.model_validate(pony_category)

    @db_session
    def update(self, cmd: UpdateCategoryCmd) -> Category:
        pony_category = PonyCategory.get(id=cmd.id)
        if not pony_category:
            raise NotFoundException(f"Category[id={cmd.id}]")

        update_data = cmd.model_dump(exclude_unset=True, exclude={"id"})

        if not update_data:
            return Category.model_validate(pony_category)

        new_slug = update_data.get("slug")
        if (
            new_slug
            and new_slug != pony_category.slug
            and PonyCategory.get(slug=new_slug)
        ):
            raise UniqueViolationException(f"Category[slug={new_slug}]")

        if "parent_id" in update_data:
            pony_category.parent = update_data["parent_id"]
            del update_data["parent_id"]

        for key, value in update_data.items():
            setattr(pony_category, key, value)

        pony_category.updated_at = datetime.now(timezone.utc)

        return Category.model_validate(pony_category)

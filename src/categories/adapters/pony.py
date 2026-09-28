from datetime import datetime, timezone
from pony.orm import db_session, select, TransactionIntegrityError, flush

from src.shared.exceptions import (
    NotFoundException,
    UniqueViolationException,
    CategoryNotEmptyException,
    InvalidCategoryParentException,
)
from src.shared.orm.models import PonyCategory
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.ports import CategoryRepository
from src.shared.pagination import Pagination


class PonyCategoryRepository(CategoryRepository):

    @classmethod
    def _to_domain(cls, category: PonyCategory) -> Category:
        # У сущности Pony поле называется parent, а не parent_id, поэтому
        # model_validate(from_attributes) молча оставлял parent_id = None.
        return Category(
            id=category.id,
            name=category.name,
            slug=category.slug,
            parent_id=category.parent.id if category.parent else None,
            created_at=category.created_at,
            children=[cls._to_domain(child) for child in category.children],
        )

    @staticmethod
    def _get_parent(parent_id: int) -> PonyCategory:
        parent = PonyCategory.get(id=parent_id)
        if not parent:
            raise NotFoundException(f"Category[id={parent_id}]")
        return parent

    @staticmethod
    def _check_no_cycle(category: PonyCategory, parent: PonyCategory) -> None:
        # Родитель не должен быть самой категорией или её потомком.
        node = parent
        while node is not None:
            if node.id == category.id:
                raise InvalidCategoryParentException(category.id, parent.id)
            node = node.parent

    @db_session
    def get_by_id(self, category_id: int) -> Category:
        category = PonyCategory.get(id=category_id)
        if not category:
            raise NotFoundException(f"Category[id={category_id}]")
        return self._to_domain(category)

    @db_session
    def get_by_slug(self, slug: str) -> Category:
        category = PonyCategory.get(slug=slug)
        if not category:
            raise NotFoundException(f"Category[slug={slug}]")
        return self._to_domain(category)

    @db_session
    def list(
        self, parent_id: int | None = None, page: Pagination | None = None
    ) -> list[Category]:
        query = select(c for c in PonyCategory)
        if parent_id is not None:
            query = query.filter(lambda c: c.parent.id == parent_id)
        query = query.order_by(PonyCategory.id)
        categories = query.limit(page.limit, page.offset) if page else query[:]
        return [self._to_domain(c) for c in categories]

    @db_session
    def create(self, cmd: CreateCategoryCmd) -> Category:
        if PonyCategory.get(slug=cmd.slug):
            raise UniqueViolationException(f"Category[slug={cmd.slug}]")
        parent = self._get_parent(cmd.parent_id) if cmd.parent_id is not None else None
        try:
            pony_category = PonyCategory(
                name=cmd.name,
                slug=cmd.slug,
                parent=parent,
                created_at=datetime.now(timezone.utc),
            )
            flush()
        except TransactionIntegrityError:
            raise UniqueViolationException(f"Category[slug={cmd.slug}]")
        return self._to_domain(pony_category)

    @db_session
    def update(self, cmd: UpdateCategoryCmd) -> Category:
        pony_category = PonyCategory.get(id=cmd.id)
        if not pony_category:
            raise NotFoundException(f"Category[id={cmd.id}]")

        update_data = cmd.model_dump(exclude_unset=True, exclude={"id"})

        if not update_data:
            return self._to_domain(pony_category)

        new_slug = update_data.get("slug")
        if (
            new_slug
            and new_slug != pony_category.slug
            and PonyCategory.get(slug=new_slug)
        ):
            raise UniqueViolationException(f"Category[slug={new_slug}]")

        if "parent_id" in update_data:
            parent_id = update_data.pop("parent_id")
            if parent_id is None:
                pony_category.parent = None
            else:
                parent = self._get_parent(parent_id)
                self._check_no_cycle(pony_category, parent)
                pony_category.parent = parent

        for key, value in update_data.items():
            setattr(pony_category, key, value)

        pony_category.updated_at = datetime.now(timezone.utc)

        return self._to_domain(pony_category)

    @db_session
    def delete(self, category_id: int) -> None:
        pony_category = PonyCategory.get(id=category_id)
        if not pony_category:
            raise NotFoundException(f"Category[id={category_id}]")
        if pony_category.products.count() or pony_category.children.count():
            raise CategoryNotEmptyException(category_id)
        pony_category.delete()

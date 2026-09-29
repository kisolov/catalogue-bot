from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.ports import CategoryRepository
from src.shared.db import Database
from src.shared.exceptions import (
    NotFoundException,
    UniqueViolationException,
    CategoryNotEmptyException,
    InvalidCategoryParentException,
)
from src.shared.orm.models import CategoryRow, ProductRow
from src.shared.pagination import Pagination


class PostgresCategoryRepository(CategoryRepository):
    def __init__(self, db: Database):
        self.db = db

    @classmethod
    def _to_domain(
        cls, row: CategoryRow, children: dict[int, list[CategoryRow]]
    ) -> Category:
        return Category(
            id=row.id,
            name=row.name,
            slug=row.slug,
            parent_id=row.parent_id,
            created_at=row.created_at,
            children=[cls._to_domain(c, children) for c in children.get(row.id, [])],
        )

    @classmethod
    async def _with_subtree(
        cls, session: AsyncSession, rows: list[CategoryRow]
    ) -> list[Category]:
        # Ленивой подгрузки в async нет, поэтому потомков читаем уровень за уровнем.
        children: dict[int, list[CategoryRow]] = {}
        seen = {row.id for row in rows}
        frontier = list(seen)
        while frontier:
            found = await session.scalars(
                select(CategoryRow)
                .where(CategoryRow.parent_id.in_(frontier))
                .order_by(CategoryRow.id)
            )
            frontier = []
            for child in found:
                children.setdefault(child.parent_id, []).append(child)
                if child.id not in seen:
                    seen.add(child.id)
                    frontier.append(child.id)
        return [cls._to_domain(row, children) for row in rows]

    @staticmethod
    async def _get_parent(session: AsyncSession, parent_id: int) -> CategoryRow:
        parent = await session.get(CategoryRow, parent_id)
        if parent is None:
            raise NotFoundException(f"Category[id={parent_id}]")
        return parent

    @staticmethod
    async def _check_no_cycle(
        session: AsyncSession, category: CategoryRow, parent: CategoryRow
    ) -> None:
        # Родитель не должен быть самой категорией или её потомком.
        node: CategoryRow | None = parent
        while node is not None:
            if node.id == category.id:
                raise InvalidCategoryParentException(category.id, parent.id)
            node = (
                await session.get(CategoryRow, node.parent_id)
                if node.parent_id is not None
                else None
            )

    async def get_by_id(self, category_id: int) -> Category:
        async with self.db.transaction() as session:
            category = await session.get(CategoryRow, category_id)
            if category is None:
                raise NotFoundException(f"Category[id={category_id}]")
            return (await self._with_subtree(session, [category]))[0]

    async def get_by_slug(self, slug: str) -> Category:
        async with self.db.transaction() as session:
            category = await session.scalar(
                select(CategoryRow).where(CategoryRow.slug == slug)
            )
            if category is None:
                raise NotFoundException(f"Category[slug={slug}]")
            return (await self._with_subtree(session, [category]))[0]

    async def list(
        self, parent_id: int | None = None, page: Pagination | None = None
    ) -> list[Category]:
        async with self.db.transaction() as session:
            query = select(CategoryRow).order_by(CategoryRow.id)
            if parent_id is not None:
                query = query.where(CategoryRow.parent_id == parent_id)
            if page:
                query = query.limit(page.limit).offset(page.offset)
            rows = list(await session.scalars(query))
            return await self._with_subtree(session, rows)

    async def create(self, cmd: CreateCategoryCmd) -> Category:
        async with self.db.transaction() as session:
            if await session.scalar(
                select(CategoryRow.id).where(CategoryRow.slug == cmd.slug)
            ):
                raise UniqueViolationException(f"Category[slug={cmd.slug}]")
            if cmd.parent_id is not None:
                await self._get_parent(session, cmd.parent_id)
            category = CategoryRow(
                name=cmd.name,
                slug=cmd.slug,
                parent_id=cmd.parent_id,
                created_at=datetime.now(timezone.utc),
            )
            session.add(category)
            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException(f"Category[slug={cmd.slug}]")
            return (await self._with_subtree(session, [category]))[0]

    async def update(self, cmd: UpdateCategoryCmd) -> Category:
        async with self.db.transaction() as session:
            category = await session.get(CategoryRow, cmd.id)
            if category is None:
                raise NotFoundException(f"Category[id={cmd.id}]")

            update_data = cmd.model_dump(exclude_unset=True, exclude={"id"})
            if not update_data:
                return (await self._with_subtree(session, [category]))[0]

            new_slug = update_data.get("slug")
            if (
                new_slug
                and new_slug != category.slug
                and await session.scalar(
                    select(CategoryRow.id).where(CategoryRow.slug == new_slug)
                )
            ):
                raise UniqueViolationException(f"Category[slug={new_slug}]")

            if "parent_id" in update_data:
                parent_id = update_data.pop("parent_id")
                if parent_id is not None:
                    parent = await self._get_parent(session, parent_id)
                    await self._check_no_cycle(session, category, parent)
                category.parent_id = parent_id

            for key, value in update_data.items():
                setattr(category, key, value)

            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException(f"Category[slug={new_slug}]")
            return (await self._with_subtree(session, [category]))[0]

    async def delete(self, category_id: int) -> None:
        async with self.db.transaction() as session:
            category = await session.get(CategoryRow, category_id)
            if category is None:
                raise NotFoundException(f"Category[id={category_id}]")
            products = await session.scalar(
                select(func.count())
                .select_from(ProductRow)
                .where(ProductRow.category_id == category_id)
            )
            children = await session.scalar(
                select(func.count())
                .select_from(CategoryRow)
                .where(CategoryRow.parent_id == category_id)
            )
            if products or children:
                raise CategoryNotEmptyException(category_id)
            await session.delete(category)

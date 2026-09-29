from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.ports import ProductRepository
from src.shared.db import Database
from src.shared.exceptions import (
    NotFoundException,
    UniqueViolationException,
    ProductInUseException,
)
from src.shared.orm.models import CategoryRow, ProductRow
from src.shared.pagination import Pagination


class PostgresProductRepository(ProductRepository):
    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _to_domain(row: ProductRow) -> Product:
        return Product(
            id=row.id,
            name=row.name,
            slug=row.slug,
            description=row.description,
            sku=row.sku,
            price=row.price,
            compare_at_price=row.compare_at_price,
            stock=row.stock,
            is_active=row.is_active,
            category_id=row.category_id,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    async def _check_uniqueness(
        session: AsyncSession, slug: str | None, sku: str | None, own_id: int | None
    ) -> None:
        if slug:
            query = select(ProductRow.id).where(ProductRow.slug == slug)
            found = await session.scalar(query)
            if found is not None and found != own_id:
                raise UniqueViolationException(f"Product[slug={slug}]")
        if sku:
            query = select(ProductRow.id).where(ProductRow.sku == sku)
            found = await session.scalar(query)
            if found is not None and found != own_id:
                raise UniqueViolationException(f"Product[sku={sku}]")

    @staticmethod
    async def _check_category(session: AsyncSession, category_id: int) -> None:
        if not await session.get(CategoryRow, category_id):
            raise NotFoundException(f"Category[id={category_id}]")

    async def get_by_id(self, product_id: int) -> Product:
        async with self.db.transaction() as session:
            product = await session.get(ProductRow, product_id)
            if product is None:
                raise NotFoundException(f"Product[id={product_id}]")
            return self._to_domain(product)

    async def get_by_slug(self, slug: str) -> Product:
        async with self.db.transaction() as session:
            product = await session.scalar(
                select(ProductRow).where(ProductRow.slug == slug)
            )
            if product is None:
                raise NotFoundException(f"Product[slug={slug}]")
            return self._to_domain(product)

    async def list(
        self,
        category_id: int | None = None,
        is_active: bool | None = True,
        page: Pagination | None = None,
    ) -> list[Product]:
        async with self.db.transaction() as session:
            query = select(ProductRow).order_by(ProductRow.id)
            if category_id is not None:
                query = query.where(ProductRow.category_id == category_id)
            if is_active is not None:
                query = query.where(ProductRow.is_active == is_active)
            if page:
                query = query.limit(page.limit).offset(page.offset)
            return [self._to_domain(p) for p in await session.scalars(query)]

    async def create(self, cmd: CreateProductCmd) -> Product:
        async with self.db.transaction() as session:
            await self._check_uniqueness(session, cmd.slug, cmd.sku, own_id=None)
            await self._check_category(session, cmd.category_id)

            now = datetime.now(timezone.utc)
            product = ProductRow(
                name=cmd.name,
                slug=cmd.slug,
                description=cmd.description,
                sku=cmd.sku,
                price=cmd.price,
                compare_at_price=cmd.compare_at_price,
                stock=cmd.stock,
                is_active=cmd.is_active,
                category_id=cmd.category_id,
                created_at=now,
                updated_at=now,
            )
            session.add(product)
            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException("Product unique constraint violation")
            return self._to_domain(product)

    async def update(self, cmd: UpdateProductCmd) -> Product:
        async with self.db.transaction() as session:
            product = await session.get(ProductRow, cmd.id)
            if product is None:
                raise NotFoundException(f"Product[id={cmd.id}]")

            update_data = cmd.model_dump(exclude_unset=True, exclude={"id"})
            if not update_data:
                return self._to_domain(product)

            await self._check_uniqueness(
                session, update_data.get("slug"), update_data.get("sku"), cmd.id
            )
            if "category_id" in update_data:
                await self._check_category(session, update_data["category_id"])

            for key, value in update_data.items():
                setattr(product, key, value)
            product.updated_at = datetime.now(timezone.utc)

            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException("Product unique constraint violation")
            return self._to_domain(product)

    async def delete(self, product_id: int) -> None:
        async with self.db.transaction() as session:
            product = await session.get(ProductRow, product_id)
            if product is None:
                raise NotFoundException(f"Product[id={product_id}]")
            try:
                # позиции заказов защищает ON DELETE RESTRICT
                await session.delete(product)
                await session.flush()
            except IntegrityError:
                raise ProductInUseException(product_id)

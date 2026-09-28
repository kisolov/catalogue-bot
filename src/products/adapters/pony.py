from datetime import datetime, timezone
from pony.orm import (
    db_session,
    TransactionIntegrityError,
    IntegrityError,
    select,
    flush,
)

from src.shared.exceptions import (
    NotFoundException,
    UniqueViolationException,
    ProductInUseException,
)
from src.shared.orm.models import PonyProduct, PonyCategory, PonyOrderItem, db
from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.ports import ProductRepository


class PonyProductRepository(ProductRepository):

    @staticmethod
    def _to_domain(pony_product: PonyProduct) -> Product:
        return Product(
            id=pony_product.id,
            name=pony_product.name,
            slug=pony_product.slug,
            description=pony_product.description,
            sku=pony_product.sku,
            price=pony_product.price,
            compare_at_price=pony_product.compare_at_price,
            stock=pony_product.stock,
            is_active=pony_product.is_active,
            category_id=pony_product.category.id,
            created_at=pony_product.created_at,
            updated_at=pony_product.updated_at,
        )

    @staticmethod
    def _check_uniqueness(slug: str, sku: str | None = None) -> None:
        if PonyProduct.get(slug=slug):
            raise UniqueViolationException(f"Product[slug={slug}]")
        if sku and PonyProduct.get(sku=sku):
            raise UniqueViolationException(f"Product[sku={sku}]")

    @staticmethod
    def _check_update_uniqueness(
        current_product: PonyProduct, new_slug: str, new_sku: str | None
    ) -> None:
        if (
            new_slug
            and new_slug != current_product.slug
            and PonyProduct.get(slug=new_slug)
        ):
            raise UniqueViolationException(f"Product[slug={new_slug}]")
        if new_sku and new_sku != current_product.sku and PonyProduct.get(sku=new_sku):
            raise UniqueViolationException(f"Product[sku={new_sku}]")

    @staticmethod
    def _get_category(category_id: int) -> PonyCategory:
        category = PonyCategory.get(id=category_id)
        if not category:
            raise NotFoundException(f"Category[id={category_id}]")
        return category

    @db_session
    def get_by_id(self, product_id: int) -> Product:
        product = PonyProduct.get(id=product_id)
        if not product:
            raise NotFoundException(f"Product[id={product_id}]")
        return self._to_domain(product)

    @db_session
    def get_by_slug(self, slug: str) -> Product:
        product = PonyProduct.get(slug=slug)
        if not product:
            raise NotFoundException(f"Product[slug={slug}]")
        return self._to_domain(product)

    @db_session
    def list(
        self,
        category_id: int | None = None,
        is_active: bool | None = True,
    ) -> list[Product]:
        query = select(p for p in PonyProduct)
        if category_id is not None:
            query = query.filter(lambda p: p.category.id == category_id)
        if is_active is not None:
            query = query.filter(lambda p: p.is_active == is_active)

        products = query[:]
        return [self._to_domain(product) for product in products]

    @db_session
    def create(self, cmd: CreateProductCmd) -> Product:
        self._check_uniqueness(cmd.slug, cmd.sku)

        try:
            pony_product = PonyProduct(
                name=cmd.name,
                slug=cmd.slug,
                description=cmd.description,
                sku=cmd.sku,
                price=cmd.price,
                compare_at_price=cmd.compare_at_price,
                stock=cmd.stock,
                is_active=cmd.is_active,
                category=self._get_category(cmd.category_id),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.flush()
        except TransactionIntegrityError:
            raise UniqueViolationException("Product unique constraint violation")

        return self._to_domain(pony_product)

    @db_session
    def update(self, cmd: UpdateProductCmd) -> Product:
        pony_product = PonyProduct.get(id=cmd.id)
        if not pony_product:
            raise NotFoundException(f"Product[id={cmd.id}]")

        update_data = cmd.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_domain(pony_product)

        self._check_update_uniqueness(
            pony_product,
            new_slug=update_data.get("slug"),
            new_sku=update_data.get("sku"),
        )

        if "category_id" in update_data:
            pony_product.category = self._get_category(update_data["category_id"])
            del update_data["category_id"]

        for key, value in update_data.items():
            setattr(pony_product, key, value)

        pony_product.updated_at = datetime.now(timezone.utc)

        return self._to_domain(pony_product)

    @db_session
    def delete(self, product_id: int) -> None:
        pony_product = PonyProduct.get(id=product_id)
        if not pony_product:
            raise NotFoundException(f"Product[id={product_id}]")
        # Pony каскадно удаляет зависимые сущности в обход ON DELETE RESTRICT,
        # поэтому проверяем заказы явно, иначе позиции заказов пропадут молча.
        if PonyOrderItem.exists(lambda item: item.product == pony_product):
            raise ProductInUseException(product_id)
        try:
            pony_product.delete()
            flush()
        except IntegrityError:
            raise ProductInUseException(product_id)

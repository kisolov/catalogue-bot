from decimal import Decimal
from typing import Optional
from faker import Faker
from src.products.models import Product, CreateProductCmd
from src.products.services import ProductService
from tests.utils.factories.category import CategoryFactory


class ProductFactory:
    def __init__(
        self,
        product_service: ProductService,
        category_factory: CategoryFactory,
    ) -> None:
        self.product_service = product_service
        self.category_factory = category_factory
        self.faker = Faker()

    def create(
        self,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        sku: Optional[str] = None,
        price: Optional[Decimal] = None,
        compare_at_price: Optional[Decimal] = None,
        stock: Optional[int] = None,
        is_active: bool = True,
        category_id: Optional[int] = None,
    ) -> Product:
        if name is None:
            name = self.faker.unique.word()
        if slug is None:
            slug = self.faker.unique.slug()
        if description is None:
            description = self.faker.sentence()
        if sku is None:
            sku = self.faker.ean(length=13)
        if price is None:
            price = Decimal(
                self.faker.pydecimal(left_digits=3, right_digits=2, positive=True)
            )
        if stock is None:
            stock = self.faker.random_int(min=0, max=100)

        if category_id is None:
            category = self.category_factory.create()
            category_id = category.id

        cmd = CreateProductCmd(
            name=name,
            slug=slug,
            description=description,
            sku=sku,
            price=price,
            compare_at_price=compare_at_price,
            stock=stock,
            is_active=is_active,
            category_id=category_id,
        )
        return self.product_service.create(cmd)

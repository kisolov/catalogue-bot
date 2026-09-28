from typing import List

from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.services import ProductService
from src.shared.logger import logger
from src.shared.pagination import Pagination


class CreateProduct:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, cmd: CreateProductCmd) -> Product:
        product = self.service.create(cmd)
        logger.info("Product created", extra={"product_id": product.id})
        return product


class UpdateProduct:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, cmd: UpdateProductCmd) -> Product:
        product = self.service.update(cmd)
        logger.info("Product updated", extra={"product_id": product.id})
        return product


class GetProductById:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, product_id: int) -> Product:
        return self.service.get_by_id(product_id)


class ListProducts:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(
        self, category_id: int | None = None, page: Pagination | None = None
    ) -> List[Product]:
        return self.service.list(category_id=category_id, page=page)


class DeleteProduct:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, product_id: int) -> None:
        self.service.delete(product_id)
        logger.info("Product deleted", extra={"product_id": product_id})

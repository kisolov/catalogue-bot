from typing import List

from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.services import ProductService


class CreateProduct:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, cmd: CreateProductCmd) -> Product:
        return self.service.create(cmd)


class UpdateProduct:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, cmd: UpdateProductCmd) -> Product:
        return self.service.update(cmd)


class GetProductById:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self, product_id: int) -> Product:
        return self.service.get_by_id(product_id)


class ListProducts:
    def __init__(self, service: ProductService):
        self.service = service

    async def __call__(self) -> List[Product]:
        return self.service.list()

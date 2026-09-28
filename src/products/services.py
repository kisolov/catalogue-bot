from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.ports import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def get_by_id(self, product_id: int) -> Product:
        return self.repo.get_by_id(product_id)

    def get_by_slug(self, slug: str) -> Product:
        return self.repo.get_by_slug(slug)

    def list(
        self, category_id: int | None = None, is_active: bool | None = True
    ) -> list[Product]:
        return self.repo.list(category_id=category_id, is_active=is_active)

    def create(self, cmd: CreateProductCmd) -> Product:
        return self.repo.create(cmd)

    def update(self, cmd: UpdateProductCmd) -> Product:
        return self.repo.update(cmd)

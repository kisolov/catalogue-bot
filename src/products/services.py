from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.ports import ProductRepository
from src.shared.exceptions import InvalidProductPriceException
from src.shared.pagination import Pagination


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def get_by_id(self, product_id: int) -> Product:
        return self.repo.get_by_id(product_id)

    def get_by_slug(self, slug: str) -> Product:
        return self.repo.get_by_slug(slug)

    def list(
        self,
        category_id: int | None = None,
        is_active: bool | None = True,
        page: Pagination | None = None,
    ) -> list[Product]:
        return self.repo.list(category_id=category_id, is_active=is_active, page=page)

    @staticmethod
    def _check_prices(price, compare_at_price) -> None:
        if compare_at_price is not None and compare_at_price < price:
            raise InvalidProductPriceException()

    def create(self, cmd: CreateProductCmd) -> Product:
        self._check_prices(cmd.price, cmd.compare_at_price)
        return self.repo.create(cmd)

    def update(self, cmd: UpdateProductCmd) -> Product:
        fields = cmd.model_dump(exclude_unset=True)
        if "price" in fields or "compare_at_price" in fields:
            current = self.repo.get_by_id(cmd.id)
            self._check_prices(
                fields.get("price", current.price),
                fields.get("compare_at_price", current.compare_at_price),
            )
        return self.repo.update(cmd)

    def delete(self, product_id: int) -> None:
        self.repo.delete(product_id)

from src.products.models import Product, CreateProductCmd, UpdateProductCmd
from src.products.ports import ProductRepository
from src.shared.exceptions import InvalidProductPriceException
from src.shared.pagination import Pagination


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def get_by_id(self, product_id: int) -> Product:
        return await self.repo.get_by_id(product_id)

    async def get_by_slug(self, slug: str) -> Product:
        return await self.repo.get_by_slug(slug)

    async def list(
        self,
        category_id: int | None = None,
        is_active: bool | None = True,
        page: Pagination | None = None,
    ) -> list[Product]:
        return await self.repo.list(
            category_id=category_id, is_active=is_active, page=page
        )

    @staticmethod
    def _check_prices(price, compare_at_price) -> None:
        if compare_at_price is not None and compare_at_price < price:
            raise InvalidProductPriceException()

    async def create(self, cmd: CreateProductCmd) -> Product:
        self._check_prices(cmd.price, cmd.compare_at_price)
        return await self.repo.create(cmd)

    async def update(self, cmd: UpdateProductCmd) -> Product:
        fields = cmd.model_dump(exclude_unset=True)
        if "price" in fields or "compare_at_price" in fields:
            current = await self.repo.get_by_id(cmd.id)
            self._check_prices(
                fields.get("price", current.price),
                fields.get("compare_at_price", current.compare_at_price),
            )
        return await self.repo.update(cmd)

    async def delete(self, product_id: int) -> None:
        await self.repo.delete(product_id)

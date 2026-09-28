from typing import Optional

from pydantic import BaseModel

from src.products.models import (
    CreateProductCmd,
    Money,
    Name,
    Sku,
    Slug,
    Stock,
)


class UpdateProductRequest(BaseModel):
    name: Optional[Name] = None
    slug: Optional[Slug] = None
    description: Optional[str] = None
    sku: Optional[Sku] = None
    price: Optional[Money] = None
    compare_at_price: Optional[Money] = None
    stock: Optional[Stock] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None


class CreateProductRequest(CreateProductCmd): ...

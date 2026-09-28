from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from src.products.models import CreateProductCmd


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None


class CreateProductRequest(CreateProductCmd): ...

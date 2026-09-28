from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    sku: Optional[str] = None

    price: Decimal
    compare_at_price: Optional[Decimal] = None
    stock: int
    is_active: bool

    category_id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateProductCmd(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    sku: Optional[str] = None

    price: Decimal
    compare_at_price: Optional[Decimal] = None
    stock: int
    is_active: bool

    category_id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateProductCmd(BaseModel):
    id: int

    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

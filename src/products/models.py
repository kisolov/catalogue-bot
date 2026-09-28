from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field

Name = Annotated[str, Field(min_length=1, max_length=200)]
Slug = Annotated[str, Field(min_length=1, max_length=200)]
Sku = Annotated[str, Field(min_length=1, max_length=50)]
Money = Annotated[Decimal, Field(ge=0, le=Decimal("99999999.99"), decimal_places=2)]
Stock = Annotated[int, Field(ge=0, le=2_147_483_647)]


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
    name: Name
    slug: Slug
    description: Optional[str] = None
    sku: Optional[Sku] = None

    price: Money
    compare_at_price: Optional[Money] = None
    stock: Stock
    is_active: bool

    category_id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateProductCmd(BaseModel):
    id: int

    name: Optional[Name] = None
    slug: Optional[Slug] = None
    description: Optional[str] = None
    sku: Optional[Sku] = None
    price: Optional[Money] = None
    compare_at_price: Optional[Money] = None
    stock: Optional[Stock] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

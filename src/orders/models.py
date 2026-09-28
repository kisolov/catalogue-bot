import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.NEW: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


class OrderItem(BaseModel):
    id: int
    order_id: int
    product_id: int

    product_name: str
    price: Decimal
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: int
    user_id: Optional[int] = None
    status: OrderStatus = OrderStatus.NEW
    total_price: Decimal
    items: List[OrderItem]

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class CreateOrderCmd(BaseModel):
    user_id: Optional[int] = None
    total_price: Decimal
    items: List[OrderItem]

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class CartItem(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    user_id: int
    items: List[CartItem]

    model_config = ConfigDict(from_attributes=True)


MAX_QUANTITY = 1000


class AddCartItemCmd(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(ge=1, le=MAX_QUANTITY)

    model_config = ConfigDict(from_attributes=True)


class RemoveCartItemCmd(BaseModel):
    user_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


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


class AddCartItemCmd(BaseModel):
    user_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class RemoveCartItemCmd(BaseModel):
    user_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)

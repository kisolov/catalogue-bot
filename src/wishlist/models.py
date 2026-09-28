from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class Favorite(BaseModel):
    id: int
    user_id: int
    product_id: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Wishlist(BaseModel):
    user_id: int
    products: List[Favorite]

    model_config = ConfigDict(from_attributes=True)


class AddInWishlistCmd(BaseModel):
    user_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)


class RemoveFromWishlistCmd(AddInWishlistCmd): ...

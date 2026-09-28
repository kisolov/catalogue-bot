from pydantic import BaseModel


class AddInWishlistRequest(BaseModel):
    product_id: int

from pydantic import BaseModel, ConfigDict


class AddInCartRequest(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict, Field


class AddInCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=1000)

    model_config = ConfigDict(from_attributes=True)

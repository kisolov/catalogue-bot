from pydantic import BaseModel

from src.orders.models import OrderStatus


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus

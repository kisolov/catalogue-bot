from decimal import Decimal
from typing import Optional, List
from faker import Faker
from src.orders.models import Order, CreateOrderCmd, OrderItem, OrderStatus
from src.orders.services import OrderService
from tests.utils.factories.product import ProductFactory
from tests.utils.factories.user import UserFactory


class OrderFactory:
    def __init__(
        self,
        order_service: OrderService,
        product_factory: ProductFactory,
        user_factory: UserFactory,
    ) -> None:
        self.order_service = order_service
        self.product_factory = product_factory
        self.user_factory = user_factory
        self.faker = Faker()

    async def create(
        self,
        user_id: Optional[int] = None,
        items: Optional[List[OrderItem]] = None,
        total_price: Optional[Decimal] = None,
        status: OrderStatus = OrderStatus.NEW,
    ) -> Order:
        if user_id is None:
            user = await self.user_factory.create()
            user_id = user.id

        if items is None:
            product = await self.product_factory.create()
            items = [
                OrderItem(
                    id=0,
                    order_id=0,
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    quantity=self.faker.random_int(min=1, max=5),
                )
            ]

        if total_price is None:
            total_price = sum(item.price * item.quantity for item in items)

        cmd = CreateOrderCmd(
            user_id=user_id,
            items=items,
            total_price=total_price,
        )
        order = await self.order_service.create(cmd)

        if status != OrderStatus.NEW:
            order.status = status
            order = await self.order_service.update(order)

        return order

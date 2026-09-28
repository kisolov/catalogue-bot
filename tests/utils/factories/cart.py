from typing import Optional, List
from faker import Faker
from src.cart.models import Cart, AddCartItemCmd
from src.cart.services import CartService
from tests.utils.factories.product import ProductFactory
from tests.utils.factories.user import UserFactory


class CartFactory:
    def __init__(
        self,
        cart_service: CartService,
        product_factory: ProductFactory,
        user_factory: UserFactory,
    ) -> None:
        self.cart_service = cart_service
        self.product_factory = product_factory
        self.user_factory = user_factory
        self.faker = Faker()

    def create(
        self,
        user_id: Optional[int] = None,
        product_ids: Optional[List[int]] = None,
        quantities: Optional[List[int]] = None,
    ) -> Cart:
        if user_id is None:
            user = self.user_factory.create()
            user_id = user.id

        if not product_ids:
            product = self.product_factory.create()
            product_ids = [product.id]
            quantities = [self.faker.random_int(min=1, max=5)]
        elif quantities is None:
            quantities = [self.faker.random_int(min=1, max=5) for _ in product_ids]

        for product_id, quantity in zip(product_ids, quantities):
            cmd = AddCartItemCmd(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
            )
            self.cart_service.add_item(cmd)

        return self.cart_service.get_by_user_id(user_id)

from typing import Optional, List
from src.wishlist.models import Wishlist, AddInWishlistCmd
from src.wishlist.services import WishlistService
from tests.utils.factories.product import ProductFactory
from tests.utils.factories.user import UserFactory


class WishlistFactory:
    def __init__(
        self,
        wishlist_service: WishlistService,
        product_factory: ProductFactory,
        user_factory: UserFactory,
    ) -> None:
        self.wishlist_service = wishlist_service
        self.product_factory = product_factory
        self.user_factory = user_factory

    def create(
        self,
        user_id: Optional[int] = None,
        product_ids: Optional[List[int]] = None,
    ) -> Wishlist:
        if user_id is None:
            user = self.user_factory.create()
            user_id = user.id

        if product_ids is None:
            product = self.product_factory.create()
            product_ids = [product.id]

        for product_id in product_ids:
            cmd = AddInWishlistCmd(
                user_id=user_id,
                product_id=product_id,
            )
            self.wishlist_service.add(cmd)

        return self.wishlist_service.get(user_id)

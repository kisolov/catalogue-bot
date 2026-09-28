import pytest

from tests.utils.factories import (
    CategoryFactory,
    UserFactory,
    ProductFactory,
    CartFactory,
    OrderFactory,
    WishlistFactory,
)


class FactoriesFixtures:
    @pytest.fixture
    def category_factory(self, container) -> CategoryFactory:
        return container.category_factory()

    @pytest.fixture
    def user_factory(self, container) -> UserFactory:
        return container.user_factory()

    @pytest.fixture
    def product_factory(self, container) -> ProductFactory:
        return container.product_factory()

    @pytest.fixture
    def cart_factory(self, container) -> CartFactory:
        return container.cart_factory()

    @pytest.fixture
    def order_factory(self, container) -> OrderFactory:
        return container.order_factory()

    @pytest.fixture
    def wishlist_factory(self, container) -> WishlistFactory:
        return container.wishlist_factory()

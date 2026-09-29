from dependency_injector import containers, providers

from di import Container
from tests.utils.test_db import TestDatabase
from tests.utils.memory_token_repo import MemoryTokenRepository
from tests.utils.factories import (
    CategoryFactory,
    UserFactory,
    ProductFactory,
    CartFactory,
    OrderFactory,
    WishlistFactory,
)
from pydantic import SecretStr

from settings import TelegramSettings
from src.auth.services import TokenService


class TestContainer(Container):
    # ---- adapters ----
    database = providers.Singleton(TestDatabase, Container.db_settings)
    token_repo = providers.Singleton(MemoryTokenRepository)

    token_service = providers.Singleton(
        TokenService, repo=token_repo, jwt_settings=Container.jwt_settings
    )

    # ---- factories ----
    category_factory = providers.Singleton(
        CategoryFactory,
        category_service=Container.category_service,
    )

    user_factory = providers.Singleton(
        UserFactory,
        user_service=Container.user_service,
    )

    product_factory = providers.Singleton(
        ProductFactory,
        product_service=Container.product_service,
        category_factory=category_factory,
    )

    cart_factory = providers.Singleton(
        CartFactory,
        cart_service=Container.cart_service,
        product_factory=product_factory,
        user_factory=user_factory,
    )

    order_factory = providers.Singleton(
        OrderFactory,
        order_service=Container.order_service,
        product_factory=product_factory,
        user_factory=user_factory,
    )

    wishlist_factory = providers.Singleton(
        WishlistFactory,
        wishlist_service=Container.wishlist_service,
        product_factory=product_factory,
        user_factory=user_factory,
    )
    telegram_settings = providers.Singleton(
        TelegramSettings, bot_token=SecretStr("123456:TEST-BOT-TOKEN")
    )
    Container.database.override(database)
    Container.telegram_settings.override(telegram_settings)
    Container.token_repo.override(token_repo)
    Container.token_service.override(token_service)


test_container = TestContainer()

# Override the main container's token_repo and token_service

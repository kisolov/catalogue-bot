from dependency_injector import containers, providers

from settings import ServerSettings, DatabaseSettings, RedisSettings, JWTSettings
from src.auth.redis_adapter import RedisTokenRepository
from src.auth.service import TokenService
from src.cart.adapters.pony import PonyCartRepository
from src.categories.adapters.pony import PonyCategoryRepository
from src.orders.adapters.pony import PonyOrderRepository
from src.products.adapters.pony import PonyProductRepository
from src.shared.orm import PonyDb
from src.users.adapters.pony import PonyUserRepository
from src.users.services import UserService
from src.products.services import ProductService
from src.categories.services import CategoryService
from src.cart.services import CartService
from src.orders.services import OrderService
from src.wishlist.adapters.pony import PonyWishlistRepository
from src.wishlist.services import WishlistService

from src.users.uc import crud as user_crud_uc
from src.products.uc import crud as product_crud_uc
from src.categories.uc import crud as category_crud_uc
from src.cart.uc import crud as cart_crud_uc
from src.orders.uc import crud as order_crud_uc
from src.wishlist.uc import crud as wishlist_crud_uc


class Container(containers.DeclarativeContainer):
    server_settings = providers.Singleton(ServerSettings)
    db_settings = providers.Singleton(DatabaseSettings)
    redis_settings = providers.Singleton(RedisSettings)
    jwt_settings = providers.Singleton(JWTSettings)

    # ---- adapters ----
    pony_db = providers.Resource(PonyDb, db_settings)

    # ---- repositories ----
    user_repo = providers.Singleton(PonyUserRepository)
    product_repo = providers.Singleton(PonyProductRepository)
    category_repo = providers.Singleton(PonyCategoryRepository)
    cart_repo = providers.Singleton(PonyCartRepository)
    order_repo = providers.Singleton(PonyOrderRepository)
    wishlist_repo = providers.Singleton(PonyWishlistRepository)
    token_repo = providers.Singleton(RedisTokenRepository, settings=redis_settings)

    # ---- services ----
    user_service = providers.Singleton(UserService, repo=user_repo)
    product_service = providers.Singleton(ProductService, repo=product_repo)
    category_service = providers.Singleton(CategoryService, repo=category_repo)
    cart_service = providers.Singleton(CartService, repo=cart_repo)
    order_service = providers.Singleton(OrderService, repo=order_repo)
    wishlist_service = providers.Singleton(WishlistService, repo=wishlist_repo)
    token_service = providers.Singleton(
        TokenService, repo=token_repo, jwt_settings=jwt_settings
    )

    # ---- use cases ----
    create_user = providers.Singleton(
        user_crud_uc.CreateUser, user_service=user_service
    )
    get_user_by_id = providers.Singleton(
        user_crud_uc.GetUserById, user_service=user_service
    )
    get_user_by_telegram_id = providers.Singleton(
        user_crud_uc.GetUserByTelegramId, user_service=user_service
    )

    create_category = providers.Singleton(
        category_crud_uc.CreateCategory, service=category_service
    )
    update_category = providers.Singleton(
        category_crud_uc.UpdateCategory, service=category_service
    )
    delete_category = providers.Singleton(
        category_crud_uc.DeleteCategory, service=category_service
    )
    get_category_by_id = providers.Singleton(
        category_crud_uc.GetCategoryById, service=category_service
    )
    list_categories = providers.Singleton(
        category_crud_uc.ListCategories, service=category_service
    )

    create_product = providers.Singleton(
        product_crud_uc.CreateProduct, service=product_service
    )
    update_product = providers.Singleton(
        product_crud_uc.UpdateProduct, service=product_service
    )
    delete_product = providers.Singleton(
        product_crud_uc.DeleteProduct, service=product_service
    )
    get_product_by_id = providers.Singleton(
        product_crud_uc.GetProductById, service=product_service
    )
    list_products = providers.Singleton(
        product_crud_uc.ListProducts, service=product_service
    )

    get_cart = providers.Singleton(cart_crud_uc.GetCart, service=cart_service)
    add_to_cart = providers.Singleton(cart_crud_uc.AddToCart, service=cart_service)
    remove_from_cart = providers.Singleton(
        cart_crud_uc.RemoveFromCart, service=cart_service
    )
    clear_cart = providers.Singleton(cart_crud_uc.ClearCart, service=cart_service)

    create_order = providers.Singleton(order_crud_uc.CreateOrder, service=order_service)
    get_order_by_id = providers.Singleton(
        order_crud_uc.GetOrderById, service=order_service
    )
    list_orders_by_user = providers.Singleton(
        order_crud_uc.ListOrdersByUser, service=order_service
    )

    add_in_wishlist = providers.Singleton(
        wishlist_crud_uc.AddInWishlist, service=wishlist_service
    )
    remove_from_wishlist = providers.Singleton(
        wishlist_crud_uc.RemoveFromWishlist, service=wishlist_service
    )
    get_wishlist = providers.Singleton(
        wishlist_crud_uc.GetWishlist, service=wishlist_service
    )


container = Container()
container.wire(packages=["src"])

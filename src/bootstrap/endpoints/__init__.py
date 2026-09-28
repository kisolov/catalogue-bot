from fastapi import APIRouter

from .users import router as users_router
from .products import router as products_router
from .categories import router as categories_router
from .cart import router as cart_router
from .wishlist import router as wishlist_router

main_router = APIRouter(responses={
        404: {"description": "Not found"},
    },)

main_router.include_router(users_router)
main_router.include_router(products_router)
main_router.include_router(categories_router)
main_router.include_router(cart_router)
main_router.include_router(wishlist_router)

__all__ = ["main_router"]

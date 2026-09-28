from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from di import Container
from src.auth.presentation import get_current_user
from src.wishlist.models import (
    Wishlist,
    Favorite,
    RemoveFromWishlistCmd,
    AddInWishlistCmd,
)
from src.users.models import User

from src.wishlist.schema import AddInWishlistRequest
from src.wishlist.uc.crud import (
    GetWishlist,
    AddInWishlist,
    RemoveFromWishlist,
)

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get(
    "/products",
    response_model=Wishlist,
    operation_id="get_products_in_wishlist",
    summary="Получить список понравившихся товаров",
)
@inject
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    uc: GetWishlist = Depends(Provide[Container.get_wishlist]),
) -> Wishlist:
    return await uc(user_id=current_user.id)


@router.post(
    "/products",
    response_model=Favorite,
    status_code=status.HTTP_201_CREATED,
    operation_id="add_in_wishlist",
    summary="Добавить товар в понравившиеся",
)
@inject
async def add_in_wishlist(
    request: AddInWishlistRequest,
    current_user: User = Depends(get_current_user),
    uc: AddInWishlist = Depends(Provide[Container.add_in_wishlist]),
) -> Favorite:
    return await uc(
        AddInWishlistCmd(product_id=request.product_id, user_id=current_user.id)
    )


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="remove_from_wishlist",
    summary="Удалить товар из понравившихся",
)
@inject
async def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    uc: RemoveFromWishlist = Depends(Provide[Container.remove_from_wishlist]),
):
    await uc(RemoveFromWishlistCmd(user_id=current_user.id, product_id=product_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

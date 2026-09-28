from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from di import container, Container
from src.cart.models import Cart, RemoveCartItemCmd, CartItem, AddCartItemCmd
from src.cart.schema import AddInCartRequest
from src.cart.uc.crud import GetCart, ClearCart
from src.users.models import User
from src.auth.presentation import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get(
    "/products",
    response_model=Cart,
    operation_id="get_products_in_cart",
    summary="Получить список товаров в корзине",
)
@inject
async def get_cart(
    current_user: User = Depends(get_current_user),
    uc: GetCart = Depends(Provide[Container.get_cart]),
) -> Cart:
    return await uc(user_id=current_user.id)


@router.delete(
    "/products",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="clear_cart",
    summary="Очистить корзину",
)
@inject
async def clear_cart(
    current_user: User = Depends(get_current_user),
    uc: ClearCart = Depends(Provide[Container.clear_cart]),
):
    await uc(user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/products",
    response_model=CartItem,
    status_code=status.HTTP_201_CREATED,
    operation_id="add_in_cart",
    summary="Добавить товар в корзину",
)
@inject
async def add_in_cart(
    request: AddInCartRequest,
    current_user: User = Depends(get_current_user),
) -> CartItem:
    uc = container.add_to_cart()
    return await uc(AddCartItemCmd(**request.model_dump(), user_id=current_user.id))


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="remove_from_cart",
    summary="Удалить товар из корзины",
)
@inject
async def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
):
    uc = container.remove_from_cart()
    await uc(RemoveCartItemCmd(user_id=current_user.id, product_id=product_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

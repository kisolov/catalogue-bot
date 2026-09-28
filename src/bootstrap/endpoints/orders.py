from typing import List

from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from di import Container
from src.bootstrap.dependencies.auth import get_current_user, get_current_admin
from src.orders.models import Order
from src.orders.schema import UpdateOrderStatusRequest
from src.orders.uc.crud import (
    CreateOrderFromCart,
    ListOrdersByUser,
    GetOrderById,
    UpdateOrderStatus,
    CancelOrder,
)
from src.users.models import User, UserRole

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_order",
    summary="Оформить заказ из корзины",
)
@inject
async def create_order(
    current_user: User = Depends(get_current_user),
    uc: CreateOrderFromCart = Depends(Provide[Container.create_order_from_cart]),
) -> Order:
    return await uc(current_user.id)


@router.get(
    "/",
    operation_id="list_my_orders",
    summary="Получить мои заказы",
)
@inject
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    uc: ListOrdersByUser = Depends(Provide[Container.list_orders_by_user]),
) -> List[Order]:
    return await uc(current_user.id)


@router.get(
    "/{order_id}",
    operation_id="get_order_by_id",
    summary="Получить заказ (свой; админ — любой)",
)
@inject
async def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    uc: GetOrderById = Depends(Provide[Container.get_order_by_id]),
) -> Order:
    return await uc(
        order_id, current_user.id, is_admin=current_user.role == UserRole.ADMIN
    )


@router.post(
    "/{order_id}/cancel",
    operation_id="cancel_order",
    summary="Отменить свой заказ (только в статусе new)",
)
@inject
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    uc: CancelOrder = Depends(Provide[Container.cancel_order]),
) -> Order:
    return await uc(order_id, current_user.id)


@router.patch(
    "/{order_id}/status",
    operation_id="update_order_status",
    summary="Сменить статус заказа (для админов)",
)
@inject
async def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    current_admin: User = Depends(get_current_admin),
    uc: UpdateOrderStatus = Depends(Provide[Container.update_order_status]),
) -> Order:
    return await uc(order_id, request.status)

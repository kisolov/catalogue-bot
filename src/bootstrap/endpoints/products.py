from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from di import Container
from src.bootstrap.dependencies.auth import get_current_admin
from src.bootstrap.dependencies.pagination import get_pagination
from src.products.models import Product, UpdateProductCmd, CreateProductCmd
from src.products.schema import UpdateProductRequest, CreateProductRequest
from src.products.uc.crud import (
    ListProducts,
    GetProductById,
    UpdateProduct,
    CreateProduct,
    DeleteProduct,
)
from src.shared.pagination import Pagination
from src.users.models import User

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "/",
    operation_id="list_products",
    summary="Получить список активных товаров (limit, offset)",
)
@inject
async def list_products(
    category_id: Optional[int] = None,
    page: Pagination = Depends(get_pagination),
    uc: ListProducts = Depends(Provide[Container.list_products]),
) -> List[Product]:
    return await uc(category_id=category_id, page=page)


@router.get(
    "/{product_id}",
    operation_id="get_product_by_id",
    summary="Получить товар по id",
)
@inject
async def get_product_by_id(
    product_id: int,
    uc: GetProductById = Depends(Provide[Container.get_product_by_id]),
) -> Product:
    return await uc(product_id)


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_product",
    summary="Создать товар (для админов)",
)
@inject
async def create_product(
    request: CreateProductRequest,
    current_admin: User = Depends(get_current_admin),
    uc: CreateProduct = Depends(Provide[Container.create_product]),
) -> Product:
    return await uc(CreateProductCmd(**request.model_dump()))


@router.patch(
    "/{product_id}",
    operation_id="update_product",
    summary="Изменить товар (для админов)",
)
@inject
async def update_product(
    product_id: int,
    request: UpdateProductRequest,
    current_admin: User = Depends(get_current_admin),
    uc: UpdateProduct = Depends(Provide[Container.update_product]),
) -> Product:
    cmd = UpdateProductCmd(id=product_id, **request.model_dump(exclude_unset=True))
    return await uc(cmd)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_product",
    summary="Удалить товар (для админов)",
)
@inject
async def delete_product(
    product_id: int,
    current_admin: User = Depends(get_current_admin),
    uc: DeleteProduct = Depends(Provide[Container.delete_product]),
) -> Response:
    await uc(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

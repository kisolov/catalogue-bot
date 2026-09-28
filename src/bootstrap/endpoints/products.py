from typing import List
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from di import Container
from src.products.models import Product, UpdateProductCmd
from src.products.schema import UpdateProductRequest
from src.products.uc.crud import ListProducts, GetProductById, UpdateProduct

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "/",
    operation_id="list_products",
    summary="Получить список всех товаров",
)
@inject
async def list_products(
    uc: ListProducts = Depends(Provide[Container.list_products]),
) -> List[Product]:
    return await uc()


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


@router.patch(
    "/{product_id}",
    operation_id="update_product",
    summary="Изменить товар",
)
@inject
async def update_product(
    product_id: int,
    request: UpdateProductRequest,
    uc: UpdateProduct = Depends(Provide[Container.update_product]),
) -> Product:
    print(request.model_dump(exclude_unset=True))
    cmd = UpdateProductCmd(id=product_id, **request.model_dump(exclude_unset=True))
    return await uc(cmd)

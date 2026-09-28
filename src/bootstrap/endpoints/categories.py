from typing import List

from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from di import Container
from src.bootstrap.dependencies.auth import get_current_admin
from src.bootstrap.dependencies.pagination import get_pagination
from src.categories.models import Category, CreateCategoryCmd, UpdateCategoryCmd
from src.categories.schema import CreateCategoryRequest, UpdateCategoryRequest
from src.categories.uc.crud import (
    ListCategories,
    GetCategoryById,
    CreateCategory,
    UpdateCategory,
    DeleteCategory,
)
from src.shared.pagination import Pagination
from src.users.models import User

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    operation_id="list_categories",
    summary="Получить список категорий (limit, offset)",
)
@inject
async def list_categories(
    page: Pagination = Depends(get_pagination),
    uc: ListCategories = Depends(Provide[Container.list_categories]),
) -> List[Category]:
    return await uc(page=page)


@router.get(
    "/{category_id}",
    operation_id="get_category_by_id",
    summary="Получить категорию по id",
)
@inject
async def get_category_by_id(
    category_id: int,
    uc: GetCategoryById = Depends(Provide[Container.get_category_by_id]),
) -> Category:
    return await uc(category_id)


@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_category",
    summary="Создать категорию (для админов)",
)
@inject
async def create_category(
    request: CreateCategoryRequest,
    current_admin: User = Depends(get_current_admin),
    uc: CreateCategory = Depends(Provide[Container.create_category]),
) -> Category:
    return await uc(CreateCategoryCmd(**request.model_dump()))


@router.patch(
    "/{category_id}",
    operation_id="update_category",
    summary="Изменить категорию (для админов)",
)
@inject
async def update_category(
    category_id: int,
    request: UpdateCategoryRequest,
    current_admin: User = Depends(get_current_admin),
    uc: UpdateCategory = Depends(Provide[Container.update_category]),
) -> Category:
    cmd = UpdateCategoryCmd(id=category_id, **request.model_dump(exclude_unset=True))
    return await uc(cmd)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_category",
    summary="Удалить пустую категорию (для админов)",
)
@inject
async def delete_category(
    category_id: int,
    current_admin: User = Depends(get_current_admin),
    uc: DeleteCategory = Depends(Provide[Container.delete_category]),
) -> Response:
    await uc(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

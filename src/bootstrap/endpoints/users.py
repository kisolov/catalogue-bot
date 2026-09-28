from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from di import Container
from src.users.models import User, CreateUserCmd
from src.users.schema import CreateUserRequest
from src.users.uc.crud import GetUserByTelegramId, GetUserById, CreateUser
from src.bootstrap.dependencies.auth import get_current_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_user",
    summary="Создать нового пользователя (для админов)",
)
@inject
async def create_user(
    request: CreateUserRequest,
    current_admin: User = Depends(get_current_admin),
    uc: CreateUser = Depends(Provide[Container.create_user]),
) -> User:
    cmd = CreateUserCmd(telegram_id=request.telegram_id, role=request.role)
    return await uc(cmd)


@router.get(
    "/{user_id}",
    response_model=User,
    operation_id="get_user_by_id",
    summary="Получить пользователя по ID (для админов)",
)
@inject
async def get_user_by_id(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    uc: GetUserById = Depends(Provide[Container.get_user_by_id]),
) -> User:
    return await uc(user_id)


@router.get(
    "/by_telegram/{telegram_id}",
    response_model=User,
    operation_id="get_user_by_telegram_id",
    summary="Получить пользователя по Telegram ID (для админов)",
)
@inject
async def get_user_by_telegram_id(
    telegram_id: int,
    current_admin: User = Depends(get_current_admin),
    uc: GetUserByTelegramId = Depends(Provide[Container.get_user_by_telegram_id]),
) -> User:
    return await uc(telegram_id)

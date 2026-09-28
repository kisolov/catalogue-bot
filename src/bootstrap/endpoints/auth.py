from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from di import Container
from src.bootstrap.dependencies.auth import get_bearer_token, get_current_user
from src.auth.schema import TelegramLoginRequest, TokenResponse
from src.auth.uc.session import GetMe
from src.auth.uc.telegram import LoginWithTelegram, Logout
from src.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/telegram",
    response_model=TokenResponse,
    operation_id="login_with_telegram",
    summary="Войти через Telegram Mini App (проверка подписи initData)",
)
@inject
async def login_with_telegram(
    request: TelegramLoginRequest,
    uc: LoginWithTelegram = Depends(Provide[Container.login_with_telegram]),
) -> TokenResponse:
    token, user = await uc(request.init_data)
    return TokenResponse(access_token=token, user=user)


@router.get(
    "/me",
    response_model=User,
    operation_id="get_me",
    summary="Текущий пользователь",
)
@inject
async def get_me(
    current_user: User = Depends(get_current_user),
    uc: GetMe = Depends(Provide[Container.get_me]),
) -> User:
    return await uc(current_user.id)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="logout",
    summary="Выйти (отозвать текущий токен)",
)
@inject
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(get_bearer_token),
    uc: Logout = Depends(Provide[Container.logout]),
) -> Response:
    await uc(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import APIKeyHeader
from dependency_injector.wiring import inject, Provide

from di import Container
from src.auth.presentation import get_current_user
from src.auth.schema import TelegramLoginRequest, TokenResponse
from src.auth.uc.telegram import LoginWithTelegram, Logout
from src.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

_authorization_header = APIKeyHeader(name="Authorization", auto_error=False)


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
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="logout",
    summary="Выйти (отозвать текущий токен)",
)
@inject
async def logout(
    current_user: User = Depends(get_current_user),
    authorization: str = Depends(_authorization_header),
    uc: Logout = Depends(Provide[Container.logout]),
) -> Response:
    await uc(authorization.removeprefix("Bearer "))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

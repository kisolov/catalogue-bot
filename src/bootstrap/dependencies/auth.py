from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.security import APIKeyHeader

from di import Container
from src.auth.uc.session import AuthenticateByToken
from src.shared.exceptions import NotAuthenticatedException, PermissionDeniedException
from src.users.models import User, UserRole

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_bearer_token(authorization: str | None = Depends(api_key_header)) -> str:
    if not authorization:
        raise NotAuthenticatedException()
    if not authorization.startswith("Bearer "):
        raise NotAuthenticatedException("Invalid authentication scheme")
    return authorization.removeprefix("Bearer ")


@inject
async def get_current_user(
    token: str = Depends(get_bearer_token),
    authenticate: AuthenticateByToken = Depends(Provide[Container.authenticate]),
) -> User:
    return await authenticate(token)


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException()
    return current_user

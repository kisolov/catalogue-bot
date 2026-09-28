from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from dependency_injector.wiring import inject, Provide

from di import Container
from src.users.models import User, UserRole
from src.users.uc.crud import GetUserById
from src.auth.service import TokenService
from src.shared.exceptions import (
    NotFoundException,
    TokenExpiredException,
    InvalidTokenException,
)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


@inject
async def get_current_user(
    token_str: str = Depends(api_key_header),
    token_service: TokenService = Depends(Provide[Container.token_service]),
    get_user_by_id: GetUserById = Depends(Provide[Container.get_user_by_id]),
) -> User:
    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if not token_str.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )

    token = token_str.removeprefix("Bearer ")

    try:
        user_id = token_service.verify_token(token)
        user = await get_user_by_id(user_id)
        return user
    except (TokenExpiredException, InvalidTokenException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required.",
        )
    return current_user

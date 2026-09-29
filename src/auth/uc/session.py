from src.auth.services import TokenService
from src.shared.exceptions import InvalidTokenException, NotFoundException
from src.users.models import User
from src.users.services import UserService


class AuthenticateByToken:
    def __init__(self, token_service: TokenService, user_service: UserService):
        self.token_service = token_service
        self.user_service = user_service

    async def __call__(self, token: str) -> User:
        user_id = await self.token_service.verify_token(token)
        try:
            return await self.user_service.get_by_id(user_id)
        except NotFoundException:
            # токен валиден, но пользователь удалён
            raise InvalidTokenException()


class GetMe:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(self, user_id: int) -> User:
        return await self.user_service.get_by_id(user_id)

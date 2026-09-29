from src.auth.services import TokenService
from src.auth.telegram import TelegramInitDataService
from src.shared.exceptions import NotFoundException, UniqueViolationException
from src.users.models import CreateUserCmd, User
from src.users.services import UserService
from src.shared.logger import logger


class LoginWithTelegram:
    def __init__(
        self,
        init_data_service: TelegramInitDataService,
        user_service: UserService,
        token_service: TokenService,
    ):
        self.init_data_service = init_data_service
        self.user_service = user_service
        self.token_service = token_service

    async def __call__(self, init_data: str) -> tuple[str, User]:
        telegram_user = self.init_data_service.validate(init_data)
        user = await self._get_or_create(telegram_user.id)
        token = await self.token_service.create_token(user.id)
        logger.info("Telegram login", extra={"user_id": user.id})
        return token, user

    async def _get_or_create(self, telegram_id: int) -> User:
        try:
            return await self.user_service.get_by_telegram_id(telegram_id)
        except NotFoundException:
            pass
        try:
            user = await self.user_service.create(
                CreateUserCmd(telegram_id=telegram_id)
            )
            logger.info("User registered via Telegram", extra={"user_id": user.id})
            return user
        except UniqueViolationException:
            # параллельный первый вход того же пользователя
            return await self.user_service.get_by_telegram_id(telegram_id)


class Logout:
    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    async def __call__(self, token: str) -> None:
        await self.token_service.revoke_token(token)
        logger.info("Logout")

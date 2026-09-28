from src.auth.service import TokenService
from src.auth.telegram import TelegramInitDataService
from src.shared.exceptions import NotFoundException, UniqueViolationException
from src.users.models import CreateUserCmd, User
from src.users.services import UserService


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
        user = self._get_or_create(telegram_user.id)
        return self.token_service.create_token(user.id), user

    def _get_or_create(self, telegram_id: int) -> User:
        try:
            return self.user_service.get_by_telegram_id(telegram_id)
        except NotFoundException:
            pass
        try:
            return self.user_service.create(CreateUserCmd(telegram_id=telegram_id))
        except UniqueViolationException:
            # параллельный первый вход того же пользователя
            return self.user_service.get_by_telegram_id(telegram_id)


class Logout:
    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    async def __call__(self, token: str) -> None:
        self.token_service.revoke_token(token)

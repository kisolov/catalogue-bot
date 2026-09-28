from src.users.models import CreateUserCmd
from src.users.services import UserService


class CreateUser:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(self, cmd: CreateUserCmd):
        return self.user_service.create(cmd)


class GetUserById:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(self, user_id: int):
        return self.user_service.get_by_id(user_id)


class GetUserByTelegramId:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(self, telegram_id: int):
        return self.user_service.get_by_telegram_id(telegram_id)

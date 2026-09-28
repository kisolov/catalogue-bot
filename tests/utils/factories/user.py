from typing import Optional
from faker import Faker
from src.users.models import User, CreateUserCmd, UserRole
from src.users.services import UserService


class UserFactory:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service
        self.faker = Faker()

    def create(
        self,
        telegram_id: Optional[int] = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        if telegram_id is None:
            telegram_id = self.faker.random_int(min=100000000, max=999999999)

        cmd = CreateUserCmd(
            telegram_id=telegram_id,
            role=role,
        )
        return self.user_service.create(cmd)

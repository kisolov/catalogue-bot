from abc import ABC, abstractmethod
from src.users.models import User, CreateUserCmd


class UserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User: ...

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User: ...

    @abstractmethod
    async def create(self, cmd: CreateUserCmd) -> User: ...

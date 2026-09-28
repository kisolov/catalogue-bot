from src.users.models import User, CreateUserCmd
from src.users.ports import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_by_id(self, user_id: int) -> User:
        return self.repo.get_by_id(user_id)

    def get_by_telegram_id(self, telegram_id: int) -> User:
        return self.repo.get_by_telegram_id(telegram_id)

    def create(self, cmd: CreateUserCmd) -> User:
        return self.repo.create(cmd)

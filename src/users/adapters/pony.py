from datetime import datetime, timezone

from pony.orm import db_session, TransactionIntegrityError, flush

from src.shared.exceptions import UniqueViolationException, NotFoundException
from src.shared.orm.models import PonyUser
from src.users.models import User, CreateUserCmd
from src.users.ports import UserRepository


class PonyUserRepository(UserRepository):
    @db_session
    def get_by_id(self, user_id: int) -> User:
        user = PonyUser.get(id=user_id)
        if not user:
            raise NotFoundException(f"User[id={user_id}]")

        return User.model_validate(user)

    @db_session
    def get_by_telegram_id(self, telegram_id: int) -> User:
        user = PonyUser.get(telegram_id=telegram_id)
        if not user:
            raise NotFoundException(f"User[telegram_id={telegram_id}]")

        return User.model_validate(user)

    @db_session
    def create(self, cmd: CreateUserCmd) -> User:
        if cmd.telegram_id is not None and PonyUser.get(telegram_id=cmd.telegram_id):
            raise UniqueViolationException(f"User[telegram_id={cmd.telegram_id}]")

        try:
            user = PonyUser(
                telegram_id=cmd.telegram_id,
                role=cmd.role.value,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            flush()
        except TransactionIntegrityError:
            raise UniqueViolationException(f"User[telegram_id={cmd.telegram_id}]")

        return User.model_validate(user)

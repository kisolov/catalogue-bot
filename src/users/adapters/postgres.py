from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.shared.db import Database
from src.shared.exceptions import UniqueViolationException, NotFoundException
from src.shared.orm.models import UserRow
from src.users.models import User, CreateUserCmd
from src.users.ports import UserRepository


class PostgresUserRepository(UserRepository):
    def __init__(self, db: Database):
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        async with self.db.transaction() as session:
            user = await session.get(UserRow, user_id)
            if user is None:
                raise NotFoundException(f"User[id={user_id}]")
            return User.model_validate(user)

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        async with self.db.transaction() as session:
            user = await session.scalar(
                select(UserRow).where(UserRow.telegram_id == telegram_id)
            )
            if user is None:
                raise NotFoundException(f"User[telegram_id={telegram_id}]")
            return User.model_validate(user)

    async def create(self, cmd: CreateUserCmd) -> User:
        async with self.db.transaction() as session:
            if cmd.telegram_id is not None and await session.scalar(
                select(UserRow.id).where(UserRow.telegram_id == cmd.telegram_id)
            ):
                raise UniqueViolationException(f"User[telegram_id={cmd.telegram_id}]")

            now = datetime.now(timezone.utc)
            user = UserRow(
                telegram_id=cmd.telegram_id,
                role=cmd.role.value,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            try:
                await session.flush()
            except IntegrityError:
                raise UniqueViolationException(f"User[telegram_id={cmd.telegram_id}]")
            return User.model_validate(user)

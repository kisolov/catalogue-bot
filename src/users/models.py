import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    id: int
    telegram_id: Optional[int] = None
    role: UserRole = UserRole.USER
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateUserCmd(BaseModel):
    telegram_id: Optional[int] = None
    role: UserRole = UserRole.USER

    model_config = ConfigDict(from_attributes=True)

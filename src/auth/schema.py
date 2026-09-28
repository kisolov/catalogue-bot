from pydantic import BaseModel

from src.users.models import User


class TelegramLoginRequest(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl

from settings import TelegramSettings
from src.shared.exceptions import InitDataExpiredException, InvalidInitDataException


@dataclass(frozen=True)
class TelegramUser:
    id: int
    first_name: str | None = None
    username: str | None = None


class TelegramInitDataService:
    """Проверка подписи initData из Telegram Mini App.

    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """

    def __init__(self, settings: TelegramSettings):
        self.settings = settings

    def validate(self, init_data: str) -> TelegramUser:
        fields = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = fields.pop("hash", None)
        if not received_hash:
            raise InvalidInitDataException("нет подписи")

        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
        secret = hmac.new(
            b"WebAppData",
            self.settings.bot_token.get_secret_value().encode(),
            hashlib.sha256,
        ).digest()
        expected = hmac.new(
            secret, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, received_hash):
            raise InvalidInitDataException()

        try:
            auth_date = int(fields["auth_date"])
            user = json.loads(fields["user"])
            user_id = int(user["id"])
        except (KeyError, ValueError, TypeError):
            raise InvalidInitDataException("нет auth_date или user")

        age = time.time() - auth_date
        if age > self.settings.init_data_max_age_seconds or age < -60:
            raise InitDataExpiredException()

        return TelegramUser(
            id=user_id,
            first_name=user.get("first_name"),
            username=user.get("username"),
        )

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class TokenRepository(ABC):
    @abstractmethod
    def save_token(self, user_id: int, token: str, expires_at: datetime) -> None: ...

    @abstractmethod
    def get_token(self, token: str) -> Optional[int]: ...

    @abstractmethod
    def revoke_token(self, token: str) -> None: ...

from typing import Dict, Optional
from src.auth.ports import TokenRepository


class MemoryTokenRepository(TokenRepository):
    def __init__(self):
        self._tokens: Dict[str, int] = {}
        self._revoked_tokens: set = set()

    async def save_token(self, user_id: int, token: str, expires_at) -> None:
        self._tokens[token] = user_id

    async def get_token(self, token: str) -> Optional[int]:
        if token in self._revoked_tokens:
            return None
        return self._tokens.get(token)

    async def revoke_token(self, token: str) -> None:
        self._revoked_tokens.add(token)
        if token in self._tokens:
            del self._tokens[token]

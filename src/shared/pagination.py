from pydantic import BaseModel, Field

MAX_LIMIT = 100
DEFAULT_LIMIT = 50


class Pagination(BaseModel):
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)

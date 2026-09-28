from fastapi import Query

from src.shared.pagination import DEFAULT_LIMIT, MAX_LIMIT, Pagination


def get_pagination(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)

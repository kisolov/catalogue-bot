from typing import Optional

from pydantic import BaseModel

from src.categories.models import CreateCategoryCmd


class CreateCategoryRequest(CreateCategoryCmd): ...


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None

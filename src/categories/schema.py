from typing import Optional

from pydantic import BaseModel

from src.categories.models import CreateCategoryCmd, Name, Slug


class CreateCategoryRequest(CreateCategoryCmd): ...


class UpdateCategoryRequest(BaseModel):
    name: Optional[Name] = None
    slug: Optional[Slug] = None
    parent_id: Optional[int] = None

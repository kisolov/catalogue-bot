from datetime import datetime
from typing import Annotated, Optional, List

from pydantic import BaseModel, ConfigDict, Field

Name = Annotated[str, Field(min_length=1, max_length=100)]
Slug = Annotated[str, Field(min_length=1, max_length=100)]


class Category(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    created_at: datetime
    children: List["Category"] = []

    model_config = ConfigDict(from_attributes=True)


class CreateCategoryCmd(BaseModel):
    name: Name
    slug: Slug
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UpdateCategoryCmd(BaseModel):
    id: int

    name: Optional[Name] = None
    slug: Optional[Slug] = None
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

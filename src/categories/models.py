from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class Category(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    created_at: datetime
    children: List["Category"] = []

    model_config = ConfigDict(from_attributes=True)


class CreateCategoryCmd(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UpdateCategoryCmd(BaseModel):
    id: int

    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

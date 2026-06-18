from pydantic import BaseModel, Field
from typing import List, Optional


class CreateRoleRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None


class UpdateRoleRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None

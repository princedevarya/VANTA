from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScopeCreate(BaseModel):
    target: str
    target_type: str
    scope_type: str = "include"
    description: str | None = None


class ScopeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    engagement_id: str
    target: str
    target_type: str
    scope_type: str
    description: str | None
    created_at: datetime
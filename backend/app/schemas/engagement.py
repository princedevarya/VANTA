from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EngagementCreate(BaseModel):
    name: str
    client: str | None = None
    description: str | None = None


class EngagementUpdate(BaseModel):
    name: str | None = None
    client: str | None = None
    description: str | None = None
    status: str | None = None


class EngagementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    client: str | None
    description: str | None
    status: str
    created_at: datetime
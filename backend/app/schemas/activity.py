from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityCreate(BaseModel):
    asset_id: str | None = None
    activity_type: str
    title: str
    description: str | None = None
    command: str | None = None
    tool: str | None = None
    status: str = "completed"


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    engagement_id: str
    asset_id: str | None
    activity_type: str
    title: str
    description: str | None
    command: str | None
    tool: str | None
    status: str
    created_at: datetime
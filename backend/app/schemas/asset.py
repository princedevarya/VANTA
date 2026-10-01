from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):
    value: str
    asset_type: str
    status: str = "discovered"
    description: str | None = None


class AssetUpdate(BaseModel):
    value: str | None = None
    asset_type: str | None = None
    status: str | None = None
    description: str | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    engagement_id: str
    value: str
    asset_type: str
    status: str
    description: str | None
    created_at: datetime
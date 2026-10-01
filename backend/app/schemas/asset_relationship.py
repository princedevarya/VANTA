from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetRelationshipCreate(BaseModel):
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    description: str | None = None


class AssetRelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    engagement_id: str
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    description: str | None
    created_at: datetime
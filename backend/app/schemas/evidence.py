from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvidenceCreate(BaseModel):
    activity_id: str | None = None
    asset_id: str | None = None
    evidence_type: str
    title: str
    content: str | None = None
    file_path: str | None = None


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    engagement_id: str
    activity_id: str | None
    asset_id: str | None
    evidence_type: str
    title: str
    content: str | None
    file_path: str | None
    created_at: datetime
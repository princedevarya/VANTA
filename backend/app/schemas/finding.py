from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FindingCreate(BaseModel):
    asset_id: str | None = None
    activity_id: str | None = None
    evidence_id: str | None = None

    title: str
    description: str | None = None

    severity: str = "informational"
    status: str = "open"
    validation_status: str = "hypothesis"

    remediation: str | None = None


class FindingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    severity: str | None = None
    status: str | None = None
    validation_status: str | None = None

    remediation: str | None = None

    retest_status: str | None = None


class RetestResult(BaseModel):
    result: str


class FindingResponse(BaseModel):
    id: str

    engagement_id: str

    asset_id: str | None
    activity_id: str | None
    evidence_id: str | None

    title: str
    description: str | None

    severity: str
    status: str
    validation_status: str

    remediation: str | None

    retest_status: str | None
    retest_activity_id: str | None
    retest_evidence_id: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
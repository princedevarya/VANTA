from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttackPathStepCreate(BaseModel):
    sequence: int = Field(
        ge=1,
    )

    step_type: str = Field(
        min_length=1,
        max_length=50,
    )

    asset_id: str | None = None

    activity_id: str | None = None

    evidence_id: str | None = None

    finding_id: str | None = None

    description: str | None = None


class AttackPathStepResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    attack_path_id: str

    sequence: int

    step_type: str

    asset_id: str | None

    activity_id: str | None

    evidence_id: str | None

    finding_id: str | None

    description: str | None

    created_at: datetime


class AttackPathCreate(BaseModel):
    engagement_id: str

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    status: str = Field(
        default="draft",
        min_length=1,
        max_length=30,
    )


class AttackPathResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    engagement_id: str

    title: str

    description: str | None

    status: str

    created_at: datetime

    steps: list[AttackPathStepResponse] = []
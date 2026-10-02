from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.attack_paths import (
    AttackPathCreate,
    AttackPathResponse,
    AttackPathStepCreate,
    AttackPathStepResponse,
)


def test_attack_path_create_accepts_valid_data():
    schema = AttackPathCreate(
        engagement_id="engagement-123",
        title="Initial compromise to internal service",
        description="Example attack path",
    )

    assert schema.engagement_id == "engagement-123"
    assert schema.title == "Initial compromise to internal service"
    assert schema.description == "Example attack path"
    assert schema.status == "draft"


def test_attack_path_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        AttackPathCreate(
            engagement_id="engagement-123",
            title="",
        )


def test_attack_path_create_rejects_title_over_255_characters():
    with pytest.raises(ValidationError):
        AttackPathCreate(
            engagement_id="engagement-123",
            title="A" * 256,
        )


def test_attack_path_step_create_accepts_provenance_references():
    schema = AttackPathStepCreate(
        sequence=1,
        step_type="finding",
        asset_id="asset-123",
        activity_id="activity-123",
        evidence_id="evidence-123",
        finding_id="finding-123",
        description="Validated authentication weakness",
    )

    assert schema.sequence == 1
    assert schema.step_type == "finding"
    assert schema.asset_id == "asset-123"
    assert schema.activity_id == "activity-123"
    assert schema.evidence_id == "evidence-123"
    assert schema.finding_id == "finding-123"


def test_attack_path_step_create_rejects_invalid_sequence():
    with pytest.raises(ValidationError):
        AttackPathStepCreate(
            sequence=0,
            step_type="asset",
        )


def test_attack_path_step_create_rejects_empty_step_type():
    with pytest.raises(ValidationError):
        AttackPathStepCreate(
            sequence=1,
            step_type="",
        )


def test_attack_path_step_response_from_model_attributes():
    created_at = datetime.utcnow()

    class FakeStep:
        id = "step-123"
        attack_path_id = "path-123"
        sequence = 1
        step_type = "asset"
        asset_id = "asset-123"
        activity_id = None
        evidence_id = None
        finding_id = None
        description = "Target asset"

    fake_step = FakeStep()
    fake_step.created_at = created_at

    schema = AttackPathStepResponse.model_validate(
        fake_step
    )

    assert schema.id == "step-123"
    assert schema.attack_path_id == "path-123"
    assert schema.sequence == 1
    assert schema.step_type == "asset"
    assert schema.asset_id == "asset-123"
    assert schema.created_at == created_at


def test_attack_path_response_from_model_attributes():
    created_at = datetime.utcnow()

    class FakeStep:
        id = "step-123"
        attack_path_id = "path-123"
        sequence = 1
        step_type = "asset"
        asset_id = "asset-123"
        activity_id = None
        evidence_id = None
        finding_id = None
        description = "Initial target"

    fake_step = FakeStep()
    fake_step.created_at = created_at

    class FakeAttackPath:
        id = "path-123"
        engagement_id = "engagement-123"
        title = "Example attack path"
        description = "Test path"
        status = "draft"
        steps = [fake_step]

    fake_attack_path = FakeAttackPath()
    fake_attack_path.created_at = created_at

    schema = AttackPathResponse.model_validate(
        fake_attack_path
    )

    assert schema.id == "path-123"
    assert schema.engagement_id == "engagement-123"
    assert schema.title == "Example attack path"
    assert schema.status == "draft"
    assert schema.created_at == created_at
    assert len(schema.steps) == 1
    assert schema.steps[0].id == "step-123"
    assert schema.steps[0].created_at == created_at
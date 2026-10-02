import pytest
from sqlalchemy import select

from app.models import (
    Activity,
    Asset,
    AttackPath,
    AttackPathStep,
    Engagement,
    Evidence,
    Finding,
)


@pytest.mark.asyncio
async def test_create_attack_path(db):
    engagement = Engagement(
        name="Attack Path Test Engagement",
        client="ACME",
        status="active",
    )

    db.add(engagement)
    await db.flush()

    attack_path = AttackPath(
        engagement_id=engagement.id,
        title="Example attack path",
        description="Initial correlated attack path",
    )

    db.add(attack_path)
    await db.commit()

    assert attack_path.id is not None
    assert attack_path.engagement_id == engagement.id
    assert attack_path.title == "Example attack path"
    assert attack_path.status == "draft"


@pytest.mark.asyncio
async def test_attack_path_steps_preserve_sequence(db):
    engagement = Engagement(
        name="Attack Path Sequence Test",
        client="ACME",
        status="active",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    db.add(asset)
    await db.flush()

    attack_path = AttackPath(
        engagement_id=engagement.id,
        title="Ordered attack path",
    )

    db.add(attack_path)
    await db.flush()

    step_one = AttackPathStep(
        attack_path_id=attack_path.id,
        sequence=1,
        step_type="asset",
        asset_id=asset.id,
        description="Primary domain",
    )

    step_two = AttackPathStep(
        attack_path_id=attack_path.id,
        sequence=2,
        step_type="asset",
        asset_id=asset.id,
        description="Follow-up asset analysis",
    )

    db.add_all([step_one, step_two])
    await db.commit()

    result = await db.execute(
        select(AttackPathStep)
        .where(
            AttackPathStep.attack_path_id
            == attack_path.id
        )
        .order_by(AttackPathStep.sequence)
    )

    steps = result.scalars().all()

    assert len(steps) == 2
    assert steps[0].sequence == 1
    assert steps[1].sequence == 2
    assert steps[0].description == "Primary domain"
    assert steps[1].description == "Follow-up asset analysis"


@pytest.mark.asyncio
async def test_attack_path_step_can_reference_provenance_objects(db):
    engagement = Engagement(
        name="Attack Path Provenance Test",
        client="ACME",
        status="active",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    db.add(asset)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Nmap service enumeration",
        tool="nmap",
        status="completed",
    )

    db.add(activity)
    await db.flush()

    evidence = Evidence(
        engagement_id=engagement.id,
        activity_id=activity.id,
        asset_id=asset.id,
        evidence_type="command_output",
        title="Nmap output",
        content="443/tcp open https",
    )

    db.add(evidence)
    await db.flush()

    finding = Finding(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_id=evidence.id,
        title="Exposed HTTPS service",
        severity="medium",
        status="open",
        validation_status="validated",
    )

    db.add(finding)
    await db.flush()

    attack_path = AttackPath(
        engagement_id=engagement.id,
        title="Evidence-backed attack path",
    )

    db.add(attack_path)
    await db.flush()

    step = AttackPathStep(
        attack_path_id=attack_path.id,
        sequence=1,
        step_type="finding",
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_id=evidence.id,
        finding_id=finding.id,
        description="Validated exposed service",
    )

    db.add(step)
    await db.commit()

    stored_step = await db.get(
        AttackPathStep,
        step.id,
    )

    assert stored_step is not None
    assert stored_step.attack_path_id == attack_path.id
    assert stored_step.asset_id == asset.id
    assert stored_step.activity_id == activity.id
    assert stored_step.evidence_id == evidence.id
    assert stored_step.finding_id == finding.id


@pytest.mark.asyncio
async def test_attack_path_steps_are_scoped_to_attack_path(db):
    engagement = Engagement(
        name="Attack Path Scope Test",
        client="ACME",
        status="active",
    )

    db.add(engagement)
    await db.flush()

    attack_path_one = AttackPath(
        engagement_id=engagement.id,
        title="Path One",
    )

    attack_path_two = AttackPath(
        engagement_id=engagement.id,
        title="Path Two",
    )

    db.add_all([
        attack_path_one,
        attack_path_two,
    ])

    await db.flush()

    step = AttackPathStep(
        attack_path_id=attack_path_one.id,
        sequence=1,
        step_type="asset",
        description="Path one step",
    )

    db.add(step)
    await db.commit()

    result_one = await db.execute(
        select(AttackPathStep).where(
            AttackPathStep.attack_path_id
            == attack_path_one.id
        )
    )

    result_two = await db.execute(
        select(AttackPathStep).where(
            AttackPathStep.attack_path_id
            == attack_path_two.id
        )
    )

    steps_one = result_one.scalars().all()
    steps_two = result_two.scalars().all()

    assert len(steps_one) == 1
    assert steps_one[0].description == "Path one step"
    assert steps_two == []


@pytest.mark.asyncio
async def test_deleting_attack_path_cascades_to_steps(db):
    engagement = Engagement(
        name="Attack Path Cascade Test",
        client="ACME",
        status="active",
    )

    db.add(engagement)
    await db.flush()

    attack_path = AttackPath(
        engagement_id=engagement.id,
        title="Cascade path",
    )

    db.add(attack_path)
    await db.flush()

    step = AttackPathStep(
        attack_path_id=attack_path.id,
        sequence=1,
        step_type="asset",
        description="Step to delete",
    )

    db.add(step)
    await db.commit()

    attack_path_id = attack_path.id
    step_id = step.id

    await db.delete(attack_path)
    await db.commit()

    stored_path = await db.get(
        AttackPath,
        attack_path_id,
    )

    stored_step = await db.get(
        AttackPathStep,
        step_id,
    )

    assert stored_path is None
    assert stored_step is None
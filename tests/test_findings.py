import pytest
from sqlalchemy import select

from app.models import (
    Activity,
    Asset,
    Engagement,
    Evidence,
    Finding,
)


@pytest.mark.asyncio
async def test_finding_lifecycle(db):
    engagement = Engagement(
        name="Test Engagement",
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
        title="Test enumeration",
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
        content="80/tcp open http",
    )

    db.add(evidence)
    await db.flush()

    finding = Finding(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_id=evidence.id,
        title="Test finding",
        severity="medium",
        validation_status="hypothesis",
        status="open",
    )

    db.add(finding)
    await db.commit()

    assert finding.validation_status == "hypothesis"
    assert finding.status == "open"

    finding.validation_status = "validated"

    await db.commit()

    assert finding.validation_status == "validated"

    retest_activity = Activity(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_type="retest",
        testing_area="validation",
        test_type="finding_retest",
        title="Retest",
        status="completed",
    )

    db.add(retest_activity)
    await db.flush()

    retest_evidence = Evidence(
        engagement_id=engagement.id,
        activity_id=retest_activity.id,
        asset_id=asset.id,
        evidence_type="retest",
        title="Retest evidence",
        content="Finding no longer reproducible",
    )

    db.add(retest_evidence)
    await db.flush()

    finding.retest_status = "passed"
    finding.retest_activity_id = retest_activity.id
    finding.retest_evidence_id = retest_evidence.id
    finding.status = "closed"

    await db.commit()

    result = await db.execute(
        select(Finding).where(
            Finding.id == finding.id
        )
    )

    stored_finding = result.scalar_one()

    assert stored_finding.validation_status == "validated"
    assert stored_finding.retest_status == "passed"
    assert stored_finding.status == "closed"
    assert stored_finding.retest_activity_id == retest_activity.id
    assert stored_finding.retest_evidence_id == retest_evidence.id


@pytest.mark.asyncio
async def test_valid_provenance_is_accepted(db):
    engagement = Engagement(
        name="Provenance Test Engagement",
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
        title="Service enumeration",
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
        content="80/tcp open http",
    )

    db.add(evidence)
    await db.flush()

    finding = Finding(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_id=evidence.id,
        title="Provenance finding",
        severity="medium",
        validation_status="hypothesis",
        status="open",
    )

    db.add(finding)
    await db.commit()

    assert finding.asset_id == asset.id
    assert finding.activity_id == activity.id
    assert finding.evidence_id == evidence.id


@pytest.mark.asyncio
async def test_evidence_must_belong_to_activity(db):
    engagement = Engagement(
        name="Provenance Test Engagement",
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

    activity_one = Activity(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="First activity",
        tool="nmap",
        status="completed",
    )

    activity_two = Activity(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_type="tool_execution",
        testing_area="web",
        test_type="input_validation",
        title="Second activity",
        tool="burp",
        status="completed",
    )

    db.add_all([
        activity_one,
        activity_two,
    ])

    await db.flush()

    evidence = Evidence(
        engagement_id=engagement.id,
        activity_id=activity_two.id,
        asset_id=asset.id,
        evidence_type="command_output",
        title="Evidence",
        content="Evidence from second activity",
    )

    db.add(evidence)
    await db.commit()

    assert evidence.activity_id == activity_two.id
    assert evidence.activity_id != activity_one.id


@pytest.mark.asyncio
async def test_activity_must_belong_to_engagement(db):
    engagement_one = Engagement(
        name="Engagement One",
    )

    engagement_two = Engagement(
        name="Engagement Two",
    )

    db.add_all([
        engagement_one,
        engagement_two,
    ])

    await db.flush()

    asset = Asset(
        engagement_id=engagement_two.id,
        value="other.example.com",
        asset_type="domain",
    )

    db.add(asset)
    await db.flush()

    activity = Activity(
        engagement_id=engagement_two.id,
        asset_id=asset.id,
        activity_type="tool_execution",
        title="Other engagement activity",
        tool="nmap",
        status="completed",
    )

    db.add(activity)
    await db.commit()

    assert activity.engagement_id == engagement_two.id
    assert activity.engagement_id != engagement_one.id


@pytest.mark.asyncio
async def test_evidence_must_belong_to_engagement(db):
    engagement_one = Engagement(
        name="Engagement One",
    )

    engagement_two = Engagement(
        name="Engagement Two",
    )

    db.add_all([
        engagement_one,
        engagement_two,
    ])

    await db.flush()

    evidence = Evidence(
        engagement_id=engagement_two.id,
        evidence_type="command_output",
        title="Other engagement evidence",
        content="Evidence",
    )

    db.add(evidence)
    await db.commit()

    assert evidence.engagement_id == engagement_two.id
    assert evidence.engagement_id != engagement_one.id


@pytest.mark.asyncio
async def test_activity_and_asset_must_match(db):
    engagement = Engagement(
        name="Provenance Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    asset_one = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    asset_two = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([
        asset_one,
        asset_two,
    ])

    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        asset_id=asset_one.id,
        activity_type="tool_execution",
        title="Asset one activity",
        tool="nmap",
        status="completed",
    )

    db.add(activity)
    await db.commit()

    assert activity.asset_id == asset_one.id
    assert activity.asset_id != asset_two.id


@pytest.mark.asyncio
async def test_evidence_and_asset_must_match(db):
    engagement = Engagement(
        name="Provenance Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    asset_one = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    asset_two = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([
        asset_one,
        asset_two,
    ])

    await db.flush()

    evidence = Evidence(
        engagement_id=engagement.id,
        asset_id=asset_one.id,
        evidence_type="command_output",
        title="Asset one evidence",
        content="Evidence",
    )

    db.add(evidence)
    await db.commit()

    assert evidence.asset_id == asset_one.id
    assert evidence.asset_id != asset_two.id


@pytest.mark.asyncio
async def test_finding_provenance_chain_is_complete(db):
    engagement = Engagement(
        name="Provenance API Test",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add(asset)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Service enumeration",
        description="Execution of nmap",
        command="nmap -sV api.example.com",
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
        description="HTTPS service discovered during enumeration",
        severity="low",
        status="open",
        validation_status="hypothesis",
    )

    db.add(finding)
    await db.commit()

    result = await db.execute(
        select(Finding).where(
            Finding.id == finding.id
        )
    )

    stored_finding = result.scalar_one()

    assert stored_finding.id == finding.id
    assert stored_finding.asset_id == asset.id
    assert stored_finding.activity_id == activity.id
    assert stored_finding.evidence_id == evidence.id

    asset_result = await db.execute(
        select(Asset).where(
            Asset.id == stored_finding.asset_id
        )
    )

    stored_asset = asset_result.scalar_one()

    activity_result = await db.execute(
        select(Activity).where(
            Activity.id == stored_finding.activity_id
        )
    )

    stored_activity = activity_result.scalar_one()

    evidence_result = await db.execute(
        select(Evidence).where(
            Evidence.id == stored_finding.evidence_id
        )
    )

    stored_evidence = evidence_result.scalar_one()

    assert stored_asset.id == stored_finding.asset_id
    assert stored_activity.id == stored_finding.activity_id
    assert stored_evidence.id == stored_finding.evidence_id

    assert stored_evidence.activity_id == stored_activity.id
    assert stored_activity.asset_id == stored_asset.id
    assert stored_evidence.asset_id == stored_asset.id


@pytest.mark.asyncio
async def test_finding_without_provenance_is_allowed(db):
    engagement = Engagement(
        name="No Provenance Test",
    )

    db.add(engagement)
    await db.flush()

    finding = Finding(
        engagement_id=engagement.id,
        title="Historical finding",
        severity="informational",
        status="open",
        validation_status="hypothesis",
    )

    db.add(finding)
    await db.commit()

    result = await db.execute(
        select(Finding).where(
            Finding.id == finding.id
        )
    )

    stored_finding = result.scalar_one()

    assert stored_finding.asset_id is None
    assert stored_finding.activity_id is None
    assert stored_finding.evidence_id is None
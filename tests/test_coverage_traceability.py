import pytest

from app.models import (
    Activity,
    Engagement,
    Evidence,
    Finding,
)
from app.services.coverage_traceability import (
    get_coverage_traceability,
)


@pytest.mark.asyncio
async def test_tested_coverage_returns_matching_activities(db):
    engagement = Engagement(
        name="Traceability Engagement",
        client="ACME",
        status="active",
    )
    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Nmap service enumeration",
        description="Service discovery",
        command="nmap -sV example.com",
        tool="nmap",
        status="completed",
    )
    db.add(activity)
    await db.commit()

    result = await get_coverage_traceability(
        db,
        engagement_id=engagement.id,
        testing_area="network",
        test_type="service_enumeration",
    )

    assert result["status"] == "tested"
    assert result["activity_count"] == 1
    assert len(result["activities"]) == 1
    assert result["activities"][0]["id"] == activity.id
    assert result["activities"][0]["tool"] == "nmap"


@pytest.mark.asyncio
async def test_evidence_is_attached_to_activity(db):
    engagement = Engagement(
        name="Evidence Traceability",
        client="ACME",
        status="active",
    )
    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
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
        evidence_type="command_output",
        title="Nmap output",
        content="80/tcp open http",
    )
    db.add(evidence)
    await db.commit()

    result = await get_coverage_traceability(
        db,
        engagement_id=engagement.id,
        testing_area="network",
        test_type="service_enumeration",
    )

    activity_result = result["activities"][0]

    assert len(activity_result["evidence"]) == 1
    assert activity_result["evidence"][0]["id"] == evidence.id
    assert activity_result["evidence"][0]["content"] == "80/tcp open http"


@pytest.mark.asyncio
async def test_finding_is_attached_through_evidence(db):
    engagement = Engagement(
        name="Finding Traceability",
        client="ACME",
        status="active",
    )
    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        activity_type="tool_execution",
        testing_area="web",
        test_type="input_validation",
        title="Input validation testing",
        tool="mock",
        status="completed",
    )
    db.add(activity)
    await db.flush()

    evidence = Evidence(
        engagement_id=engagement.id,
        activity_id=activity.id,
        evidence_type="command_output",
        title="Validation evidence",
        content="Observed reflected input",
    )
    db.add(evidence)
    await db.flush()

    finding = Finding(
        engagement_id=engagement.id,
        activity_id=activity.id,
        evidence_id=evidence.id,
        title="Reflected input",
        severity="medium",
        status="open",
        validation_status="validated",
    )
    db.add(finding)
    await db.commit()

    result = await get_coverage_traceability(
        db,
        engagement_id=engagement.id,
        testing_area="web",
        test_type="input_validation",
    )

    activity_result = result["activities"][0]
    evidence_result = activity_result["evidence"][0]

    assert len(activity_result["findings"]) == 1
    assert activity_result["findings"][0]["id"] == finding.id

    assert len(evidence_result["findings"]) == 1
    assert evidence_result["findings"][0]["id"] == finding.id


@pytest.mark.asyncio
async def test_untested_coverage_returns_empty_activities(db):
    engagement = Engagement(
        name="Untested Engagement",
        client="ACME",
        status="active",
    )
    db.add(engagement)
    await db.commit()

    result = await get_coverage_traceability(
        db,
        engagement_id=engagement.id,
        testing_area="api",
        test_type="rate_limiting",
    )

    assert result["status"] == "untested"
    assert result["activity_count"] == 0
    assert result["activities"] == []


@pytest.mark.asyncio
async def test_failed_activity_does_not_count_as_tested(db):
    engagement = Engagement(
        name="Failed Activity Engagement",
        client="ACME",
        status="active",
    )
    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="port_enumeration",
        title="Port scan",
        tool="nmap",
        status="failed",
    )
    db.add(activity)
    await db.commit()

    result = await get_coverage_traceability(
        db,
        engagement_id=engagement.id,
        testing_area="network",
        test_type="port_enumeration",
    )

    assert result["status"] == "untested"
    assert result["activity_count"] == 0
    assert result["activities"] == []


@pytest.mark.asyncio
async def test_other_engagement_activity_does_not_leak(db):
    engagement_one = Engagement(
        name="Engagement One",
        client="ACME",
        status="active",
    )

    engagement_two = Engagement(
        name="Engagement Two",
        client="OTHER",
        status="active",
    )

    db.add_all(
        [
            engagement_one,
            engagement_two,
        ]
    )
    await db.flush()

    activity = Activity(
        engagement_id=engagement_two.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Other engagement scan",
        tool="nmap",
        status="completed",
    )

    db.add(activity)
    await db.commit()

    result = await get_coverage_traceability(
        db,
        engagement_id=engagement_one.id,
        testing_area="network",
        test_type="service_enumeration",
    )

    assert result["status"] == "untested"
    assert result["activity_count"] == 0
    assert result["activities"] == []
import pytest
from pathlib import Path

from app.models import (
    Activity,
    Asset,
    Engagement,
    Evidence,
    Finding,
    Scope,
    Service,
)
from app.services.report_generator import generate_report
from app.services.coverage import get_testing_coverage


@pytest.mark.asyncio
async def test_dashboard_data(db):
    engagement = Engagement(
        name="Dashboard Test",
        client="Test Client",
        status="active",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    scope = Scope(
        engagement_id=engagement.id,
        target="example.com",
        target_type="domain",
        scope_type="include",
    )

    db.add(asset)
    db.add(scope)
    await db.flush()

    service = Service(
        engagement_id=engagement.id,
        asset_id=asset.id,
        port=443,
        protocol="tcp",
        state="open",
        service="https",
    )

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

    evidence = Evidence(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_type="command_output",
        title="Nmap output",
        content="443/tcp open https",
    )

    db.add(service)
    db.add(activity)
    db.add(evidence)

    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement.id,
    )

    assert coverage["network"]["service_enumeration"] == "tested"

    assert coverage["network"]["port_enumeration"] == "untested"


@pytest.mark.asyncio
async def test_report_generation(db):
    engagement = Engagement(
        name="Report Test",
        client="Test Client",
        description="Testing report generation",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    scope = Scope(
        engagement_id=engagement.id,
        target="example.com",
        target_type="domain",
        scope_type="include",
    )

    activity = Activity(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Nmap scan",
        tool="nmap",
        status="completed",
    )

    evidence = Evidence(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_type="command_output",
        title="Nmap output",
        content="443/tcp open https",
    )

    finding = Finding(
        engagement_id=engagement.id,
        asset_id=asset.id,
        activity_id=activity.id,
        evidence_id=evidence.id,
        title="Test finding",
        description="Test vulnerability",
        severity="medium",
        status="open",
        validation_status="validated",
        remediation="Apply remediation",
    )

    db.add(asset)
    db.add(scope)
    db.add(activity)
    db.add(evidence)
    db.add(finding)

    await db.commit()

    filename, report_path = await generate_report(
        db,
        engagement_id=engagement.id,
    )

    assert filename == "Report_Test_report.md"

    assert Path(report_path).exists()

    content = Path(report_path).read_text(
        encoding="utf-8"
    )

    assert "# VANTA Penetration Testing Report" in content
    assert "Report Test" in content
    assert "example.com" in content
    assert "Test finding" in content
    assert "Test vulnerability" in content
    assert "Apply remediation" in content
    assert "service_enumeration" in content
    assert "443/tcp open https" in content
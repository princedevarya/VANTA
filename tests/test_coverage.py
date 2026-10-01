import pytest

from app.models import Activity, Engagement
from app.services.coverage import (
    TESTING_TAXONOMY,
    get_testing_coverage,
)


@pytest.mark.asyncio
async def test_empty_engagement_has_no_tested_coverage(db):
    engagement = Engagement(
        name="Coverage Test Engagement",
    )

    db.add(engagement)
    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement.id,
    )

    for area, test_types in TESTING_TAXONOMY.items():
        for test_type in test_types:
            assert coverage[area][test_type] == "untested"


@pytest.mark.asyncio
async def test_completed_activity_marks_test_as_tested(db):
    engagement = Engagement(
        name="Coverage Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Nmap service enumeration",
        tool="nmap",
        status="completed",
    )

    db.add(activity)
    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement.id,
    )

    assert coverage["network"]["service_enumeration"] == "tested"
    assert coverage["network"]["port_enumeration"] == "untested"


@pytest.mark.asyncio
async def test_failed_activity_does_not_mark_tested(db):
    engagement = Engagement(
        name="Coverage Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Failed Nmap service enumeration",
        tool="nmap",
        status="failed",
    )

    db.add(activity)
    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement.id,
    )

    assert coverage["network"]["service_enumeration"] == "untested"


@pytest.mark.asyncio
async def test_duplicate_activities_do_not_change_coverage(db):
    engagement = Engagement(
        name="Coverage Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    activities = [
        Activity(
            engagement_id=engagement.id,
            activity_type="tool_execution",
            testing_area="network",
            test_type="service_enumeration",
            title="First enumeration",
            tool="nmap",
            status="completed",
        ),
        Activity(
            engagement_id=engagement.id,
            activity_type="tool_execution",
            testing_area="network",
            test_type="service_enumeration",
            title="Second enumeration",
            tool="nmap",
            status="completed",
        ),
    ]

    db.add_all(activities)
    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement.id,
    )

    assert coverage["network"]["service_enumeration"] == "tested"


@pytest.mark.asyncio
async def test_unknown_testing_area_does_not_corrupt_coverage(db):
    engagement = Engagement(
        name="Coverage Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    activity = Activity(
        engagement_id=engagement.id,
        activity_type="manual_test",
        testing_area="unknown_area",
        test_type="unknown_test",
        title="Unknown test",
        status="completed",
    )

    db.add(activity)
    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement.id,
    )

    for area, test_types in TESTING_TAXONOMY.items():
        for test_type in test_types:
            assert coverage[area][test_type] == "untested"


@pytest.mark.asyncio
async def test_activity_from_another_engagement_does_not_affect_coverage(db):
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

    activity = Activity(
        engagement_id=engagement_one.id,
        activity_type="tool_execution",
        testing_area="network",
        test_type="service_enumeration",
        title="Nmap service enumeration",
        tool="nmap",
        status="completed",
    )

    db.add(activity)
    await db.commit()

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement_two.id,
    )

    assert coverage["network"]["service_enumeration"] == "untested"
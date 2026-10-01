from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity


TESTING_TAXONOMY = {
    "recon": [
        "dns",
        "subdomain_discovery",
        "technology_discovery",
    ],
    "network": [
        "port_enumeration",
        "service_enumeration",
        "network_configuration",
    ],
    "web": [
        "authentication",
        "authorization",
        "session_management",
        "input_validation",
        "business_logic",
    ],
    "api": [
        "authentication",
        "authorization",
        "object_level_authorization",
        "rate_limiting",
        "input_validation",
    ],
}


async def get_testing_coverage(
    db: AsyncSession,
    *,
    engagement_id: str,
):
    result = await db.execute(
        select(
            Activity.testing_area,
            Activity.test_type,
        ).where(
            Activity.engagement_id == engagement_id,
            Activity.status == "completed",
        )
    )

    activities = result.all()

    tested = {
        (testing_area, test_type)
        for testing_area, test_type in activities
        if testing_area and test_type
    }

    coverage = {}

    for area, test_types in TESTING_TAXONOMY.items():
        coverage[area] = {}

        for test_type in test_types:
            coverage[area][test_type] = (
                "tested"
                if (area, test_type) in tested
                else "untested"
            )

    return coverage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.evidence import Evidence
from app.models.finding import Finding


async def get_coverage_traceability(
    db: AsyncSession,
    *,
    engagement_id: str,
    testing_area: str,
    test_type: str,
):
    activity_result = await db.execute(
        select(Activity)
        .where(
            Activity.engagement_id == engagement_id,
            Activity.testing_area == testing_area,
            Activity.test_type == test_type,
            Activity.status == "completed",
        )
        .order_by(Activity.created_at.desc())
    )

    activities = activity_result.scalars().all()

    activity_ids = [activity.id for activity in activities]

    evidence_by_activity = {}

    if activity_ids:
        evidence_result = await db.execute(
            select(Evidence)
            .where(
                Evidence.engagement_id == engagement_id,
                Evidence.activity_id.in_(activity_ids),
            )
            .order_by(Evidence.created_at.desc())
        )

        for evidence in evidence_result.scalars().all():
            evidence_by_activity.setdefault(
                evidence.activity_id,
                [],
            ).append(evidence)

    finding_result = await db.execute(
        select(Finding)
        .where(
            Finding.engagement_id == engagement_id,
        )
        .order_by(Finding.created_at.desc())
    )

    findings = finding_result.scalars().all()

    findings_by_activity = {}
    findings_by_evidence = {}

    for finding in findings:
        if finding.activity_id:
            findings_by_activity.setdefault(
                finding.activity_id,
                [],
            ).append(finding)

        if finding.evidence_id:
            findings_by_evidence.setdefault(
                finding.evidence_id,
                [],
            ).append(finding)

    activity_items = []

    for activity in activities:
        evidence_items = evidence_by_activity.get(
            activity.id,
            [],
        )

        evidence_payload = []

        for evidence in evidence_items:
            evidence_findings = findings_by_evidence.get(
                evidence.id,
                [],
            )

            evidence_payload.append(
                {
                    "id": evidence.id,
                    "evidence_type": evidence.evidence_type,
                    "title": evidence.title,
                    "content": evidence.content,
                    "file_path": evidence.file_path,
                    "created_at": evidence.created_at,
                    "findings": [
                        {
                            "id": finding.id,
                            "title": finding.title,
                            "severity": finding.severity,
                            "status": finding.status,
                            "validation_status": (
                                finding.validation_status
                            ),
                        }
                        for finding in evidence_findings
                    ],
                }
            )

        activity_findings = findings_by_activity.get(
            activity.id,
            [],
        )

        activity_items.append(
            {
                "id": activity.id,
                "asset_id": activity.asset_id,
                "activity_type": activity.activity_type,
                "testing_area": activity.testing_area,
                "test_type": activity.test_type,
                "title": activity.title,
                "description": activity.description,
                "command": activity.command,
                "tool": activity.tool,
                "status": activity.status,
                "created_at": activity.created_at,
                "evidence": evidence_payload,
                "findings": [
                    {
                        "id": finding.id,
                        "title": finding.title,
                        "severity": finding.severity,
                        "status": finding.status,
                        "validation_status": (
                            finding.validation_status
                        ),
                    }
                    for finding in activity_findings
                ],
            }
        )

    return {
        "engagement_id": engagement_id,
        "testing_area": testing_area,
        "test_type": test_type,
        "status": "tested" if activities else "untested",
        "activity_count": len(activities),
        "activities": activity_items,
    }
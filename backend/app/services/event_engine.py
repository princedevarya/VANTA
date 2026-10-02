from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Evidence, Finding, FindingEvidence
from app.services.adapters.base import ToolResult
from app.services.detection.finding_detector import detect_findings


async def process_tool_result(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str | None,
    result: ToolResult,
    title: str,
    testing_area: str | None = None,
    test_type: str | None = None,
):
    # ---------------------------------------------------------
    # 1. Record the tool execution
    # ---------------------------------------------------------
    activity = Activity(
        engagement_id=engagement_id,
        asset_id=asset_id,
        activity_type="tool_execution",
        testing_area=testing_area,
        test_type=test_type,
        title=title,
        description=f"Execution of {result.tool}",
        command=result.command,
        tool=result.tool,
        status="completed" if result.return_code == 0 else "failed",
    )

    db.add(activity)
    await db.flush()

    # ---------------------------------------------------------
    # 2. Store raw tool output as evidence
    # ---------------------------------------------------------
    evidence = Evidence(
        engagement_id=engagement_id,
        activity_id=activity.id,
        asset_id=asset_id,
        evidence_type="command_output",
        title=f"{result.tool} output",
        content=result.output,
    )

    db.add(evidence)
    await db.flush()

    # ---------------------------------------------------------
    # 3. Detect finding candidates
    # ---------------------------------------------------------
    finding_candidates = []

    if result.return_code == 0:
        finding_candidates = detect_findings(
            testing_area=testing_area,
            test_type=test_type,
            output=result.output,
        )

    # ---------------------------------------------------------
    # 4. Correlate findings and supporting evidence
    # ---------------------------------------------------------
    findings = []

    for candidate in finding_candidates:
        existing_result = await db.execute(
            select(Finding).where(
                Finding.engagement_id == engagement_id,
                Finding.asset_id == asset_id,
                Finding.title == candidate.title,
                Finding.status == "open",
                Finding.validation_status == "hypothesis",
            )
        )

        existing_finding = existing_result.scalar_one_or_none()

        if existing_finding is not None:
            finding = existing_finding

            # Prevent duplicate FindingEvidence links
            relationship_result = await db.execute(
                select(FindingEvidence).where(
                    FindingEvidence.finding_id == finding.id,
                    FindingEvidence.evidence_id == evidence.id,
                )
            )

            relationship = relationship_result.scalar_one_or_none()

            if relationship is None:
                db.add(
                    FindingEvidence(
                        finding_id=finding.id,
                        evidence_id=evidence.id,
                        relationship_type="supporting",
                    )
                )

        else:
            finding = Finding(
                engagement_id=engagement_id,
                asset_id=asset_id,
                activity_id=activity.id,
                evidence_id=evidence.id,
                title=candidate.title,
                description=candidate.description,
                severity=candidate.severity,
                status="open",
                validation_status="hypothesis",
                remediation=candidate.remediation,
            )

            db.add(finding)
            await db.flush()

            # Link the first evidence through the relationship table
            db.add(
                FindingEvidence(
                    finding_id=finding.id,
                    evidence_id=evidence.id,
                    relationship_type="supporting",
                )
            )

        findings.append(finding)

    # ---------------------------------------------------------
    # 5. Commit everything atomically
    # ---------------------------------------------------------
    await db.commit()

    await db.refresh(activity)
    await db.refresh(evidence)

    for finding in findings:
        await db.refresh(finding)

    return {
        "activity": activity,
        "evidence": evidence,
        "findings": findings,
    }
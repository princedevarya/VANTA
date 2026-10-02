from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity
from app.models.asset import Asset
from app.models.engagement import Engagement
from app.models.evidence import Evidence
from app.models.finding import Finding
from app.models.finding_evidence import FindingEvidence
from app.schemas.finding import (
    FindingCreate,
    FindingResponse,
    FindingUpdate,
    RetestResult,
)


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Findings"],
)


async def get_finding_or_404(
    db: AsyncSession,
    engagement_id: str,
    finding_id: str,
) -> Finding:
    result = await db.execute(
        select(Finding).where(
            Finding.id == finding_id,
            Finding.engagement_id == engagement_id,
        )
    )

    finding = result.scalar_one_or_none()

    if finding is None:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    return finding


async def validate_provenance(
    db: AsyncSession,
    engagement_id: str,
    asset_id: str | None,
    activity_id: str | None,
    evidence_id: str | None,
) -> None:
    asset = None
    activity = None
    evidence = None

    if asset_id is not None:
        result = await db.execute(
            select(Asset).where(
                Asset.id == asset_id,
                Asset.engagement_id == engagement_id,
            )
        )

        asset = result.scalar_one_or_none()

        if asset is None:
            raise HTTPException(
                status_code=404,
                detail="Asset not found in this engagement",
            )

    if activity_id is not None:
        result = await db.execute(
            select(Activity).where(
                Activity.id == activity_id,
                Activity.engagement_id == engagement_id,
            )
        )

        activity = result.scalar_one_or_none()

        if activity is None:
            raise HTTPException(
                status_code=404,
                detail="Activity not found in this engagement",
            )

    if evidence_id is not None:
        result = await db.execute(
            select(Evidence).where(
                Evidence.id == evidence_id,
                Evidence.engagement_id == engagement_id,
            )
        )

        evidence = result.scalar_one_or_none()

        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail="Evidence not found in this engagement",
            )

    if activity is not None and evidence is not None:
        if evidence.activity_id != activity.id:
            raise HTTPException(
                status_code=400,
                detail="Evidence does not belong to the supplied activity",
            )

    if asset is not None and activity is not None:
        if (
            activity.asset_id is not None
            and activity.asset_id != asset.id
        ):
            raise HTTPException(
                status_code=400,
                detail="Activity does not belong to the supplied asset",
            )

    if asset is not None and evidence is not None:
        if (
            evidence.asset_id is not None
            and evidence.asset_id != asset.id
        ):
            raise HTTPException(
                status_code=400,
                detail="Evidence does not belong to the supplied asset",
            )

    if activity is not None and evidence is not None:
        if (
            activity.asset_id is not None
            and evidence.asset_id is not None
            and activity.asset_id != evidence.asset_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Activity and evidence belong to different assets",
            )


@router.post(
    "/{engagement_id}/findings",
    response_model=FindingResponse,
    status_code=201,
)
async def create_finding(
    engagement_id: str,
    data: FindingCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Engagement).where(
            Engagement.id == engagement_id,
        )
    )

    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found",
        )

    await validate_provenance(
        db=db,
        engagement_id=engagement_id,
        asset_id=data.asset_id,
        activity_id=data.activity_id,
        evidence_id=data.evidence_id,
    )

    finding = Finding(
        engagement_id=engagement_id,
        asset_id=data.asset_id,
        activity_id=data.activity_id,
        evidence_id=data.evidence_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=data.status,
        validation_status=data.validation_status,
        remediation=data.remediation,
    )

    db.add(finding)

    await db.commit()
    await db.refresh(finding)

    return finding


@router.get(
    "/{engagement_id}/findings",
    response_model=list[FindingResponse],
)
async def list_findings(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Finding)
        .where(
            Finding.engagement_id == engagement_id,
        )
        .order_by(Finding.created_at.desc())
    )

    return result.scalars().all()


@router.get(
    "/{engagement_id}/findings/{finding_id}",
    response_model=FindingResponse,
)
async def get_finding(
    engagement_id: str,
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )


@router.get(
    "/{engagement_id}/findings/{finding_id}/provenance",
)
async def get_finding_provenance(
    engagement_id: str,
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):
    finding = await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )

    asset = None
    activity = None
    evidence = None

    if finding.asset_id is not None:
        result = await db.execute(
            select(Asset).where(
                Asset.id == finding.asset_id,
                Asset.engagement_id == engagement_id,
            )
        )

        asset = result.scalar_one_or_none()

    if finding.activity_id is not None:
        result = await db.execute(
            select(Activity).where(
                Activity.id == finding.activity_id,
                Activity.engagement_id == engagement_id,
            )
        )

        activity = result.scalar_one_or_none()

    if finding.evidence_id is not None:
        result = await db.execute(
            select(Evidence).where(
                Evidence.id == finding.evidence_id,
                Evidence.engagement_id == engagement_id,
            )
        )

        evidence = result.scalar_one_or_none()

    return {
        "finding": {
            "id": finding.id,
            "title": finding.title,
            "severity": finding.severity,
            "status": finding.status,
            "validation_status": finding.validation_status,
        },
        "asset": (
            {
                "id": asset.id,
                "value": asset.value,
                "asset_type": asset.asset_type,
            }
            if asset is not None
            else None
        ),
        "activity": (
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "testing_area": activity.testing_area,
                "test_type": activity.test_type,
                "title": activity.title,
                "description": activity.description,
                "command": activity.command,
                "tool": activity.tool,
                "status": activity.status,
                "created_at": activity.created_at,
            }
            if activity is not None
            else None
        ),
        "evidence": (
            {
                "id": evidence.id,
                "evidence_type": evidence.evidence_type,
                "title": evidence.title,
                "content": evidence.content,
                "file_path": evidence.file_path,
                "created_at": evidence.created_at,
            }
            if evidence is not None
            else None
        ),
    }


@router.get(
    "/{engagement_id}/findings/{finding_id}/evidence",
)
async def get_finding_evidence(
    engagement_id: str,
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):
    await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )

    result = await db.execute(
        select(
            FindingEvidence,
            Evidence,
        )
        .join(
            Evidence,
            Evidence.id == FindingEvidence.evidence_id,
        )
        .where(
            FindingEvidence.finding_id == finding_id,
            Evidence.engagement_id == engagement_id,
        )
        .order_by(
            FindingEvidence.created_at.asc()
        )
    )

    rows = result.all()

    return [
        {
            "id": relationship.id,
            "finding_id": relationship.finding_id,
            "evidence_id": relationship.evidence_id,
            "relationship_type": relationship.relationship_type,
            "created_at": relationship.created_at,
            "evidence": {
                "id": evidence.id,
                "activity_id": evidence.activity_id,
                "asset_id": evidence.asset_id,
                "evidence_type": evidence.evidence_type,
                "title": evidence.title,
                "content": evidence.content,
                "file_path": evidence.file_path,
                "created_at": evidence.created_at,
            },
        }
        for relationship, evidence in rows
    ]


@router.patch(
    "/{engagement_id}/findings/{finding_id}",
    response_model=FindingResponse,
)
async def update_finding(
    engagement_id: str,
    finding_id: str,
    data: FindingUpdate,
    db: AsyncSession = Depends(get_db),
):
    finding = await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )

    updates = data.model_dump(
        exclude_unset=True,
    )

    for field, value in updates.items():
        setattr(finding, field, value)

    await db.commit()
    await db.refresh(finding)

    return finding


@router.post(
    "/{engagement_id}/findings/{finding_id}/validate",
    response_model=FindingResponse,
)
async def validate_finding(
    engagement_id: str,
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):
    finding = await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )

    finding.validation_status = "validated"

    await db.commit()
    await db.refresh(finding)

    return finding


@router.post(
    "/{engagement_id}/findings/{finding_id}/retest",
    response_model=FindingResponse,
)
async def retest_finding(
    engagement_id: str,
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):
    finding = await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )

    if finding.validation_status != "validated":
        raise HTTPException(
            status_code=400,
            detail="Finding must be validated before retesting",
        )

    if finding.asset_id is None:
        raise HTTPException(
            status_code=400,
            detail="Finding has no associated asset",
        )

    activity = Activity(
        engagement_id=engagement_id,
        asset_id=finding.asset_id,
        activity_type="retest",
        testing_area="validation",
        test_type="finding_retest",
        title=f"Retest: {finding.title}",
        description=f"Retest performed for finding: {finding.title}",
        status="completed",
    )

    db.add(activity)
    await db.flush()

    evidence = Evidence(
        engagement_id=engagement_id,
        activity_id=activity.id,
        asset_id=finding.asset_id,
        evidence_type="retest",
        title=f"Retest evidence: {finding.title}",
        content=(
            "Retest activity recorded. "
            "Manual verification is required to determine "
            "whether the finding is still reproducible."
        ),
    )

    db.add(evidence)
    await db.flush()

    finding.retest_status = "pending"
    finding.retest_activity_id = activity.id
    finding.retest_evidence_id = evidence.id

    await db.commit()
    await db.refresh(finding)

    return finding


@router.post(
    "/{engagement_id}/findings/{finding_id}/retest/result",
    response_model=FindingResponse,
)
async def set_retest_result(
    engagement_id: str,
    finding_id: str,
    data: RetestResult,
    db: AsyncSession = Depends(get_db),
):
    finding = await get_finding_or_404(
        db,
        engagement_id,
        finding_id,
    )

    if data.result not in {"passed", "failed"}:
        raise HTTPException(
            status_code=400,
            detail="Retest result must be 'passed' or 'failed'",
        )

    if finding.retest_activity_id is None:
        raise HTTPException(
            status_code=400,
            detail="No retest has been performed for this finding",
        )

    finding.retest_status = data.result

    if data.result == "passed":
        finding.status = "closed"
    else:
        finding.status = "open"

    await db.commit()
    await db.refresh(finding)

    return finding
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity
from app.models.asset import Asset
from app.models.engagement import Engagement
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate, EvidenceResponse


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Evidence"],
)


@router.post(
    "/{engagement_id}/evidence",
    response_model=EvidenceResponse,
    status_code=201,
)
async def create_evidence(
    engagement_id: str,
    data: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Engagement).where(
            Engagement.id == engagement_id
        )
    )

    engagement = result.scalar_one_or_none()

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found",
        )

    if data.activity_id:
        result = await db.execute(
            select(Activity).where(
                Activity.id == data.activity_id,
                Activity.engagement_id == engagement_id,
            )
        )

        activity = result.scalar_one_or_none()

        if activity is None:
            raise HTTPException(
                status_code=404,
                detail="Activity not found in this engagement",
            )

    if data.asset_id:
        result = await db.execute(
            select(Asset).where(
                Asset.id == data.asset_id,
                Asset.engagement_id == engagement_id,
            )
        )

        asset = result.scalar_one_or_none()

        if asset is None:
            raise HTTPException(
                status_code=404,
                detail="Asset not found in this engagement",
            )

    evidence = Evidence(
        engagement_id=engagement_id,
        activity_id=data.activity_id,
        asset_id=data.asset_id,
        evidence_type=data.evidence_type,
        title=data.title,
        content=data.content,
        file_path=data.file_path,
    )

    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)

    return evidence


@router.get(
    "/{engagement_id}/evidence",
    response_model=list[EvidenceResponse],
)
async def list_evidence(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Evidence)
        .where(Evidence.engagement_id == engagement_id)
        .order_by(Evidence.created_at.desc())
    )

    return result.scalars().all()
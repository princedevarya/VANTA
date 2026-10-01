from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.activity import Activity
from app.models.asset import Asset
from app.models.engagement import Engagement
from app.schemas.activity import ActivityCreate, ActivityResponse


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Activities"],
)


@router.post(
    "/{engagement_id}/activities",
    response_model=ActivityResponse,
    status_code=201,
)
async def create_activity(
    engagement_id: str,
    data: ActivityCreate,
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

    activity = Activity(
        engagement_id=engagement_id,
        asset_id=data.asset_id,
        activity_type=data.activity_type,
        title=data.title,
        description=data.description,
        command=data.command,
        tool=data.tool,
        status=data.status,
    )

    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    return activity


@router.get(
    "/{engagement_id}/activities",
    response_model=list[ActivityResponse],
)
async def list_activities(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity)
        .where(Activity.engagement_id == engagement_id)
        .order_by(Activity.created_at.desc())
    )

    return result.scalars().all()
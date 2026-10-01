from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.engagement import Engagement
from app.schemas.engagement import (
    EngagementCreate,
    EngagementResponse,
    EngagementUpdate,
)


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Engagements"],
)


@router.post(
    "",
    response_model=EngagementResponse,
    status_code=201,
)
async def create_engagement(
    data: EngagementCreate,
    db: AsyncSession = Depends(get_db),
):
    engagement = Engagement(
        name=data.name,
        client=data.client,
        description=data.description,
    )

    db.add(engagement)
    await db.commit()
    await db.refresh(engagement)

    return engagement


@router.get(
    "",
    response_model=list[EngagementResponse],
)
async def list_engagements(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Engagement).order_by(Engagement.created_at.desc())
    )

    return result.scalars().all()


@router.get(
    "/{engagement_id}",
    response_model=EngagementResponse,
)
async def get_engagement(
    engagement_id: str,
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

    return engagement


@router.patch(
    "/{engagement_id}",
    response_model=EngagementResponse,
)
async def update_engagement(
    engagement_id: str,
    data: EngagementUpdate,
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

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(engagement, field, value)

    await db.commit()
    await db.refresh(engagement)

    return engagement


@router.delete(
    "/{engagement_id}",
    status_code=204,
)
async def delete_engagement(
    engagement_id: str,
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

    await db.delete(engagement)
    await db.commit()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Engagement, Service

router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Services"],
)


@router.get("/{engagement_id}/services")
async def list_services(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    # Verify engagement exists
    engagement_result = await db.execute(
        select(Engagement).where(
            Engagement.id == engagement_id
        )
    )

    engagement = engagement_result.scalar_one_or_none()

    if engagement is None:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found",
        )

    # Get discovered services
    result = await db.execute(
        select(Service)
        .where(Service.engagement_id == engagement_id)
        .order_by(Service.port)
    )

    services = result.scalars().all()

    return services
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Engagement, HttpService


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["http-services"],
)


@router.get("/{engagement_id}/http-services")
async def list_http_services(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
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

    result = await db.execute(
        select(HttpService)
        .where(
            HttpService.engagement_id == engagement_id
        )
        .order_by(HttpService.created_at.desc())
    )

    services = result.scalars().all()

    return [
        {
            "id": service.id,
            "engagement_id": service.engagement_id,
            "asset_id": service.asset_id,
            "url": service.url,
            "scheme": service.scheme,
            "host": service.host,
            "port": service.port,
            "status_code": service.status_code,
            "title": service.title,
            "webserver": service.webserver,
            "source_activity_id": service.source_activity_id,
            "source_evidence_id": service.source_evidence_id,
            "created_at": service.created_at,
        }
        for service in services
    ]
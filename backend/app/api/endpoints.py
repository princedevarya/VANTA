from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Asset, Endpoint, Engagement


router = APIRouter(
    prefix="/api/v1/endpoints",
    tags=["Endpoints"],
)


def serialize_endpoint(endpoint: Endpoint) -> dict:
    return {
        "id": endpoint.id,
        "engagement_id": endpoint.engagement_id,
        "asset_id": endpoint.asset_id,
        "url": endpoint.url,
        "method": endpoint.method,
        "scheme": endpoint.scheme,
        "host": endpoint.host,
        "port": endpoint.port,
        "path": endpoint.path,
        "query": endpoint.query,
        "status_code": endpoint.status_code,
        "content_type": endpoint.content_type,
        "server": endpoint.server,
        "source_url": endpoint.source_url,
        "tag": endpoint.tag,
        "attribute": endpoint.attribute,
        "source_activity_id": endpoint.source_activity_id,
        "source_evidence_id": endpoint.source_evidence_id,
        "created_at": endpoint.created_at,
    }


@router.get("/engagement/{engagement_id}")
async def list_engagement_endpoints(
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
        select(Endpoint)
        .where(
            Endpoint.engagement_id == engagement_id
        )
        .order_by(Endpoint.host, Endpoint.path, Endpoint.method)
    )

    endpoints = result.scalars().all()

    return {
        "engagement_id": engagement_id,
        "count": len(endpoints),
        "endpoints": [
            serialize_endpoint(endpoint)
            for endpoint in endpoints
        ],
    }


@router.get("/asset/{asset_id}")
async def list_asset_endpoints(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    asset_result = await db.execute(
        select(Asset).where(
            Asset.id == asset_id
        )
    )

    asset = asset_result.scalar_one_or_none()

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    result = await db.execute(
        select(Endpoint)
        .where(
            Endpoint.asset_id == asset_id
        )
        .order_by(Endpoint.path, Endpoint.method)
    )

    endpoints = result.scalars().all()

    return {
        "asset_id": asset_id,
        "asset": asset.value,
        "count": len(endpoints),
        "endpoints": [
            serialize_endpoint(endpoint)
            for endpoint in endpoints
        ],
    }
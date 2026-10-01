from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.models.engagement import Engagement
from app.schemas.asset import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
)


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Assets"],
)


@router.post(
    "/{engagement_id}/assets",
    response_model=AssetResponse,
    status_code=201,
)
async def create_asset(
    engagement_id: str,
    data: AssetCreate,
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

    asset = Asset(
        engagement_id=engagement_id,
        value=data.value,
        asset_type=data.asset_type,
        status=data.status,
        description=data.description,
    )

    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return asset


@router.get(
    "/{engagement_id}/assets",
    response_model=list[AssetResponse],
)
async def list_assets(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Asset)
        .where(Asset.engagement_id == engagement_id)
        .order_by(Asset.created_at)
    )

    return result.scalars().all()


@router.get(
    "/{engagement_id}/assets/{asset_id}",
    response_model=AssetResponse,
)
async def get_asset(
    engagement_id: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
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
            detail="Asset not found",
        )

    return asset


@router.patch(
    "/{engagement_id}/assets/{asset_id}",
    response_model=AssetResponse,
)
async def update_asset(
    engagement_id: str,
    asset_id: str,
    data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
):
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
            detail="Asset not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(asset, field, value)

    await db.commit()
    await db.refresh(asset)

    return asset


@router.delete(
    "/{engagement_id}/assets/{asset_id}",
    status_code=204,
)
async def delete_asset(
    engagement_id: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
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
            detail="Asset not found",
        )

    await db.delete(asset)
    await db.commit()
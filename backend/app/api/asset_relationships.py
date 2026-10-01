from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.models.asset_relationship import AssetRelationship
from app.schemas.asset_relationship import (
    AssetRelationshipCreate,
    AssetRelationshipResponse,
)


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Asset Relationships"],
)


@router.post(
    "/{engagement_id}/relationships",
    response_model=AssetRelationshipResponse,
    status_code=201,
)
async def create_asset_relationship(
    engagement_id: str,
    data: AssetRelationshipCreate,
    db: AsyncSession = Depends(get_db),
):
    if data.source_asset_id == data.target_asset_id:
        raise HTTPException(
            status_code=400,
            detail="Source and target assets must be different",
        )

    relationship_type = data.relationship_type.strip()

    if not relationship_type:
        raise HTTPException(
            status_code=400,
            detail="Relationship type cannot be empty",
        )

    result = await db.execute(
        select(Asset).where(
            Asset.id.in_(
                [
                    data.source_asset_id,
                    data.target_asset_id,
                ]
            ),
            Asset.engagement_id == engagement_id,
        )
    )

    assets = result.scalars().all()

    asset_ids = {asset.id for asset in assets}

    if data.source_asset_id not in asset_ids:
        raise HTTPException(
            status_code=404,
            detail="Source asset not found",
        )

    if data.target_asset_id not in asset_ids:
        raise HTTPException(
            status_code=404,
            detail="Target asset not found",
        )

    existing_result = await db.execute(
        select(AssetRelationship).where(
            AssetRelationship.engagement_id == engagement_id,
            AssetRelationship.source_asset_id
            == data.source_asset_id,
            AssetRelationship.target_asset_id
            == data.target_asset_id,
            AssetRelationship.relationship_type
            == relationship_type,
        )
    )

    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Asset relationship already exists",
        )

    relationship = AssetRelationship(
        engagement_id=engagement_id,
        source_asset_id=data.source_asset_id,
        target_asset_id=data.target_asset_id,
        relationship_type=relationship_type,
        description=data.description,
    )

    db.add(relationship)

    await db.commit()
    await db.refresh(relationship)

    return relationship


@router.get(
    "/{engagement_id}/relationships",
    response_model=list[AssetRelationshipResponse],
)
async def list_asset_relationships(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AssetRelationship)
        .where(
            AssetRelationship.engagement_id
            == engagement_id
        )
        .order_by(
            AssetRelationship.created_at
        )
    )

    return result.scalars().all()


@router.delete(
    "/{engagement_id}/relationships/{relationship_id}",
    status_code=204,
)
async def delete_asset_relationship(
    engagement_id: str,
    relationship_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AssetRelationship).where(
            AssetRelationship.id == relationship_id,
            AssetRelationship.engagement_id
            == engagement_id,
        )
    )

    relationship = result.scalar_one_or_none()

    if relationship is None:
        raise HTTPException(
            status_code=404,
            detail="Asset relationship not found",
        )

    await db.delete(relationship)
    await db.commit()
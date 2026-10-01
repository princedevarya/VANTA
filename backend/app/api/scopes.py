from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.engagement import Engagement
from app.models.scope import Scope
from app.schemas.scope import ScopeCreate, ScopeResponse


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Scope"],
)


@router.post(
    "/{engagement_id}/scope",
    response_model=ScopeResponse,
    status_code=201,
)
async def create_scope(
    engagement_id: str,
    data: ScopeCreate,
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

    if data.scope_type not in {"include", "exclude"}:
        raise HTTPException(
            status_code=400,
            detail="scope_type must be 'include' or 'exclude'",
        )

    scope = Scope(
        engagement_id=engagement_id,
        target=data.target,
        target_type=data.target_type,
        scope_type=data.scope_type,
        description=data.description,
    )

    db.add(scope)
    await db.commit()
    await db.refresh(scope)

    return scope


@router.get(
    "/{engagement_id}/scope",
    response_model=list[ScopeResponse],
)
async def list_scope(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scope)
        .where(Scope.engagement_id == engagement_id)
        .order_by(Scope.created_at)
    )

    return result.scalars().all()
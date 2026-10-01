from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Asset, Scope


async def resolve_asset_target(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str,
) -> str:
    # 1. Resolve asset and verify ownership
    result = await db.execute(
        select(Asset).where(
            Asset.id == asset_id,
            Asset.engagement_id == engagement_id,
        )
    )

    asset = result.scalar_one_or_none()

    if asset is None:
        raise ValueError(
            "Asset does not exist or does not belong to this engagement"
        )

    # 2. Explicit exclusions always win
    excluded_result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id,
            Scope.target == asset.value,
            Scope.scope_type == "exclude",
        )
    )

    excluded_scope = excluded_result.scalar_one_or_none()

    if excluded_scope is not None:
        raise ValueError(
            f"Asset '{asset.value}' is explicitly excluded from scope"
        )

    # 3. Asset must be explicitly included
    included_result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id,
            Scope.target == asset.value,
            Scope.scope_type == "include",
        )
    )

    included_scope = included_result.scalar_one_or_none()

    if included_scope is None:
        raise ValueError(
            f"Asset '{asset.value}' is not included in engagement scope"
        )

    return asset.value
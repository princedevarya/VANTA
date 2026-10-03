from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Asset, AssetRelationship, Scope


def normalize_domain(value: str) -> str:
    return value.strip().lower().rstrip(".")


def wildcard_matches(scope_target: str, target: str) -> bool:
    scope_target = normalize_domain(scope_target)
    target = normalize_domain(target)

    if not scope_target.startswith("*."):
        return scope_target == target

    suffix = scope_target[2:]

    return target.endswith("." + suffix) and target != suffix


async def is_discovered_asset_in_scope(
    db: AsyncSession,
    *,
    engagement_id: str,
    value: str,
) -> bool:
    """
    Check whether a discovered domain is allowed by the engagement.

    Include scopes define what may be discovered.
    Exclude scopes always override includes.
    """
    normalized_value = normalize_domain(value)

    result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id,
        )
    )
    scopes = result.scalars().all()

    excluded = any(
        scope.scope_type == "exclude"
        and wildcard_matches(scope.target, normalized_value)
        for scope in scopes
    )

    if excluded:
        return False

    included = any(
        scope.scope_type == "include"
        and wildcard_matches(scope.target, normalized_value)
        for scope in scopes
    )

    return included


async def get_or_create_discovery_seed(
    db: AsyncSession,
    *,
    engagement_id: str,
    target: str,
) -> Asset:
    """
    Resolve or create the Asset representing a discovery seed.

    Example:

        scope: *.example.com
        discovery target: example.com

    The discovery seed is represented as an Asset so that the
    resulting Activity, Evidence, and discovered Asset relationships
    all have a concrete provenance anchor.
    """
    normalized_target = normalize_domain(target)

    result = await db.execute(
        select(Asset).where(
            Asset.engagement_id == engagement_id,
            Asset.value == normalized_target,
            Asset.asset_type == "domain",
        )
    )

    existing = result.scalar_one_or_none()

    if existing is not None:
        return existing

    seed = Asset(
        engagement_id=engagement_id,
        value=normalized_target,
        asset_type="domain",
        status="discovered",
        description="Discovery seed",
    )

    db.add(seed)
    await db.flush()

    return seed


async def store_discovered_subdomains(
    db: AsyncSession,
    *,
    engagement_id: str,
    parent_asset_id: str,
    subdomains: list[str],
) -> list[Asset]:
    """
    Persist discovered subdomains as scoped Assets.

    Every discovered asset is linked back to the discovery seed
    through an AssetRelationship(discovered_from).

    Out-of-scope discoveries are discarded.
    Existing assets are reused.
    """
    parent_result = await db.execute(
        select(Asset).where(
            Asset.id == parent_asset_id,
            Asset.engagement_id == engagement_id,
        )
    )
    parent_asset = parent_result.scalar_one_or_none()

    if parent_asset is None:
        raise ValueError("Discovery seed asset not found")

    discovered_assets: list[Asset] = []

    normalized_values: list[str] = []

    for value in subdomains:
        normalized = normalize_domain(value)

        if not normalized:
            continue

        if normalized == normalize_domain(parent_asset.value):
            continue

        if normalized not in normalized_values:
            normalized_values.append(normalized)

    for value in normalized_values:
        if not await is_discovered_asset_in_scope(
            db,
            engagement_id=engagement_id,
            value=value,
        ):
            continue

        result = await db.execute(
            select(Asset).where(
                Asset.engagement_id == engagement_id,
                Asset.value == value,
                Asset.asset_type == "subdomain",
            )
        )

        asset = result.scalar_one_or_none()

        if asset is None:
            asset = Asset(
                engagement_id=engagement_id,
                value=value,
                asset_type="subdomain",
                status="discovered",
                description="Discovered through subdomain enumeration",
            )

            db.add(asset)
            await db.flush()

        relationship_result = await db.execute(
            select(AssetRelationship).where(
                AssetRelationship.engagement_id == engagement_id,
                AssetRelationship.source_asset_id == parent_asset.id,
                AssetRelationship.target_asset_id == asset.id,
                AssetRelationship.relationship_type == "discovered_from",
            )
        )

        relationship = relationship_result.scalar_one_or_none()

        if relationship is None:
            db.add(
                AssetRelationship(
                    engagement_id=engagement_id,
                    source_asset_id=parent_asset.id,
                    target_asset_id=asset.id,
                    relationship_type="discovered_from",
                    description="Discovered during subdomain enumeration",
                )
            )

        discovered_assets.append(asset)

    await db.commit()

    for asset in discovered_assets:
        await db.refresh(asset)

    return discovered_assets
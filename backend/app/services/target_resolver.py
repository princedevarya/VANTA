from fnmatch import fnmatch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Asset, Scope


def normalize_target(value: str) -> str:
    return value.strip().lower().rstrip(".")


def scope_matches(scope_target: str, asset_target: str) -> bool:
    scope_target = normalize_target(scope_target)
    asset_target = normalize_target(asset_target)

    if scope_target == asset_target:
        return True

    if scope_target.startswith("*."):
        return fnmatch(asset_target, scope_target)

    return False


async def resolve_asset_target(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str,
) -> str:
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

    asset_target = normalize_target(asset.value)

    scopes_result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id,
        )
    )

    scopes = scopes_result.scalars().all()

    for scope in scopes:
        if (
            scope.scope_type == "exclude"
            and scope_matches(scope.target, asset_target)
        ):
            raise ValueError(
                f"Asset '{asset.value}' is explicitly excluded from scope"
            )

    for scope in scopes:
        if (
            scope.scope_type == "include"
            and scope_matches(scope.target, asset_target)
        ):
            return asset.value

    raise ValueError(
        f"Asset '{asset.value}' is not included in engagement scope"
    )


async def resolve_discovery_target(
    db: AsyncSession,
    *,
    engagement_id: str,
    target: str,
) -> str:
    """
    Resolve a discovery seed.

    Discovery seeds may be the apex domain corresponding to a wildcard
    subdomain scope, because the seed is used to discover authorized
    subdomains rather than being treated as a test asset.
    """
    normalized = normalize_target(target)

    if not normalized:
        raise ValueError("Discovery target cannot be empty")

    scopes_result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id,
        )
    )

    scopes = scopes_result.scalars().all()

    for scope in scopes:
        if scope.scope_type != "include":
            continue

        scope_target = normalize_target(scope.target)

        if scope_target == normalized:
            break

        if scope_target.startswith("*."):
            wildcard_base = scope_target[2:]

            if normalized == wildcard_base:
                break
    else:
        raise ValueError(
            f"Discovery target '{target}' does not correspond "
            "to an included engagement scope"
        )

    for scope in scopes:
        if (
            scope.scope_type == "exclude"
            and normalize_target(scope.target) == normalized
        ):
            raise ValueError(
                f"Discovery target '{target}' is explicitly excluded"
            )

    return normalized
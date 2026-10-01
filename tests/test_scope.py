import pytest

from app.models import Asset, Engagement, Scope
from app.services.target_resolver import resolve_asset_target


@pytest.mark.asyncio
async def test_included_asset_is_resolvable(db):
    engagement = Engagement(
        name="Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    scope = Scope(
        engagement_id=engagement.id,
        target="example.com",
        target_type="domain",
        scope_type="include",
    )

    db.add(asset)
    db.add(scope)

    await db.commit()

    target = await resolve_asset_target(
        db,
        engagement_id=engagement.id,
        asset_id=asset.id,
    )

    assert target == "example.com"


@pytest.mark.asyncio
async def test_excluded_asset_is_rejected(db):
    engagement = Engagement(
        name="Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="admin.example.com",
        asset_type="subdomain",
    )

    scope = Scope(
        engagement_id=engagement.id,
        target="admin.example.com",
        target_type="domain",
        scope_type="exclude",
    )

    db.add(asset)
    db.add(scope)

    await db.commit()

    with pytest.raises(ValueError, match="explicitly excluded"):
        await resolve_asset_target(
            db,
            engagement_id=engagement.id,
            asset_id=asset.id,
        )
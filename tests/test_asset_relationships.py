import pytest

from app.api.asset_relationships import (
    create_asset_relationship,
    delete_asset_relationship,
    list_asset_relationships,
)
from app.models import Asset, AssetRelationship, Engagement
from app.schemas.asset_relationship import (
    AssetRelationshipCreate,
)


@pytest.mark.asyncio
async def test_create_asset_relationship(db):
    engagement = Engagement(
        name="Relationship Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    source = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    target = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([source, target])
    await db.flush()

    relationship = await create_asset_relationship(
        engagement_id=engagement.id,
        data=AssetRelationshipCreate(
            source_asset_id=source.id,
            target_asset_id=target.id,
            relationship_type="related_to",
            description="API discovered as part of the primary domain attack surface",
        ),
        db=db,
    )

    assert relationship.id is not None
    assert relationship.engagement_id == engagement.id
    assert relationship.source_asset_id == source.id
    assert relationship.target_asset_id == target.id
    assert relationship.relationship_type == "related_to"


@pytest.mark.asyncio
async def test_list_asset_relationships(db):
    engagement = Engagement(
        name="Relationship Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    source = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    target = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([source, target])
    await db.flush()

    relationship = AssetRelationship(
        engagement_id=engagement.id,
        source_asset_id=source.id,
        target_asset_id=target.id,
        relationship_type="related_to",
    )

    db.add(relationship)
    await db.commit()

    relationships = await list_asset_relationships(
        engagement_id=engagement.id,
        db=db,
    )

    assert len(relationships) == 1
    assert relationships[0].source_asset_id == source.id
    assert relationships[0].target_asset_id == target.id


@pytest.mark.asyncio
async def test_relationship_cannot_connect_asset_to_itself(db):
    engagement = Engagement(
        name="Relationship Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    asset = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    db.add(asset)
    await db.flush()

    with pytest.raises(Exception) as exc_info:
        await create_asset_relationship(
            engagement_id=engagement.id,
            data=AssetRelationshipCreate(
                source_asset_id=asset.id,
                target_asset_id=asset.id,
                relationship_type="related_to",
            ),
            db=db,
        )

    assert "different" in str(exc_info.value)


@pytest.mark.asyncio
async def test_relationship_rejects_asset_from_another_engagement(
    db,
):
    engagement_one = Engagement(
        name="Engagement One",
    )

    engagement_two = Engagement(
        name="Engagement Two",
    )

    db.add_all([
        engagement_one,
        engagement_two,
    ])

    await db.flush()

    source = Asset(
        engagement_id=engagement_one.id,
        value="example.com",
        asset_type="domain",
    )

    target = Asset(
        engagement_id=engagement_two.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([source, target])
    await db.flush()

    with pytest.raises(Exception) as exc_info:
        await create_asset_relationship(
            engagement_id=engagement_one.id,
            data=AssetRelationshipCreate(
                source_asset_id=source.id,
                target_asset_id=target.id,
                relationship_type="related_to",
            ),
            db=db,
        )

    assert "Target asset not found" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_duplicate_relationship_is_rejected(db):
    engagement = Engagement(
        name="Relationship Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    source = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    target = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([source, target])
    await db.flush()

    data = AssetRelationshipCreate(
        source_asset_id=source.id,
        target_asset_id=target.id,
        relationship_type="related_to",
    )

    await create_asset_relationship(
        engagement_id=engagement.id,
        data=data,
        db=db,
    )

    with pytest.raises(Exception) as exc_info:
        await create_asset_relationship(
            engagement_id=engagement.id,
            data=data,
            db=db,
        )

    assert "already exists" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_delete_asset_relationship(db):
    engagement = Engagement(
        name="Relationship Test Engagement",
    )

    db.add(engagement)
    await db.flush()

    source = Asset(
        engagement_id=engagement.id,
        value="example.com",
        asset_type="domain",
    )

    target = Asset(
        engagement_id=engagement.id,
        value="api.example.com",
        asset_type="subdomain",
    )

    db.add_all([source, target])
    await db.flush()

    relationship = AssetRelationship(
        engagement_id=engagement.id,
        source_asset_id=source.id,
        target_asset_id=target.id,
        relationship_type="related_to",
    )

    db.add(relationship)
    await db.commit()

    relationship_id = relationship.id

    await delete_asset_relationship(
        engagement_id=engagement.id,
        relationship_id=relationship_id,
        db=db,
    )

    result = await db.get(
        AssetRelationship,
        relationship_id,
    )

    assert result is None
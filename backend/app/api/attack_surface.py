from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import (
    Activity,
    Asset,
    Engagement,
    Evidence,
    Finding,
    Scope,
    Service,
)
from app.services.coverage import get_testing_coverage


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Attack Surface"],
)


@router.get("/{engagement_id}/assets/{asset_id}/attack-surface")
async def get_asset_attack_surface(
    engagement_id: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    asset_result = await db.execute(
        select(Asset).where(
            Asset.id == asset_id,
            Asset.engagement_id == engagement_id,
        )
    )

    asset = asset_result.scalar_one_or_none()

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    services_result = await db.execute(
        select(Service)
        .where(
            Service.asset_id == asset_id,
            Service.engagement_id == engagement_id,
        )
        .order_by(Service.port)
    )

    services = services_result.scalars().all()

    activities_result = await db.execute(
        select(Activity)
        .where(
            Activity.asset_id == asset_id,
            Activity.engagement_id == engagement_id,
        )
        .order_by(Activity.created_at.desc())
    )

    activities = activities_result.scalars().all()

    evidence_result = await db.execute(
        select(Evidence)
        .where(
            Evidence.asset_id == asset_id,
            Evidence.engagement_id == engagement_id,
        )
        .order_by(Evidence.created_at.desc())
    )

    evidence = evidence_result.scalars().all()

    findings_result = await db.execute(
        select(Finding)
        .where(
            Finding.asset_id == asset_id,
            Finding.engagement_id == engagement_id,
        )
        .order_by(Finding.created_at.desc())
    )

    findings = findings_result.scalars().all()

    return {
        "asset": {
            "id": asset.id,
            "value": asset.value,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "description": asset.description,
        },
        "services": [
            {
                "id": service.id,
                "port": service.port,
                "protocol": service.protocol,
                "state": service.state,
                "service": service.service,
                "created_at": service.created_at,
            }
            for service in services
        ],
        "activities": [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "testing_area": activity.testing_area,
                "test_type": activity.test_type,
                "title": activity.title,
                "tool": activity.tool,
                "command": activity.command,
                "status": activity.status,
                "created_at": activity.created_at,
            }
            for activity in activities
        ],
        "evidence": [
            {
                "id": item.id,
                "activity_id": item.activity_id,
                "evidence_type": item.evidence_type,
                "title": item.title,
                "created_at": item.created_at,
            }
            for item in evidence
        ],
        "findings": [
            {
                "id": finding.id,
                "title": finding.title,
                "severity": finding.severity,
                "status": finding.status,
                "validation_status": finding.validation_status,
                "evidence_id": finding.evidence_id,
                "created_at": finding.created_at,
            }
            for finding in findings
        ],
    }


@router.get("/{engagement_id}/attack-surface/summary")
async def get_attack_surface_summary(
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

    assets_result = await db.execute(
        select(Asset).where(
            Asset.engagement_id == engagement_id
        )
    )

    assets = assets_result.scalars().all()

    scopes_result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id
        )
    )

    scopes = scopes_result.scalars().all()

    included_targets = {
        scope.target
        for scope in scopes
        if scope.scope_type == "include"
    }

    excluded_targets = {
        scope.target
        for scope in scopes
        if scope.scope_type == "exclude"
    }

    in_scope_assets = [
        asset
        for asset in assets
        if asset.value in included_targets
        and asset.value not in excluded_targets
    ]

    excluded_assets = [
        asset
        for asset in assets
        if asset.value in excluded_targets
    ]

    services_result = await db.execute(
        select(Service).where(
            Service.engagement_id == engagement_id
        )
    )

    services = services_result.scalars().all()

    activities_result = await db.execute(
        select(Activity).where(
            Activity.engagement_id == engagement_id
        )
    )

    activities = activities_result.scalars().all()

    evidence_result = await db.execute(
        select(Evidence).where(
            Evidence.engagement_id == engagement_id
        )
    )

    evidence = evidence_result.scalars().all()

    findings_result = await db.execute(
        select(Finding).where(
            Finding.engagement_id == engagement_id
        )
    )

    findings = findings_result.scalars().all()

    in_scope_asset_ids = {
        asset.id
        for asset in in_scope_assets
    }

    in_scope_services = [
        service
        for service in services
        if service.asset_id in in_scope_asset_ids
    ]

    open_services = [
        service
        for service in in_scope_services
        if service.state == "open"
    ]

    http_services = [
        service
        for service in open_services
        if service.service.lower() == "http"
    ]

    https_services = [
        service
        for service in open_services
        if service.service.lower() in {
            "https",
            "ssl/http",
            "ssl/https",
        }
    ]

    validated_findings = [
        finding
        for finding in findings
        if finding.validation_status == "validated"
    ]

    return {
        "engagement": {
            "id": engagement.id,
            "name": engagement.name,
            "status": engagement.status,
        },
        "summary": {
            "total_assets": len(assets),
            "in_scope_assets": len(in_scope_assets),
            "excluded_assets": len(excluded_assets),
            "total_services": len(services),
            "in_scope_services": len(in_scope_services),
            "open_services": len(open_services),
            "http_services": len(http_services),
            "https_services": len(https_services),
            "activities": len(activities),
            "evidence_items": len(evidence),
            "findings": len(findings),
            "validated_findings": len(validated_findings),
        },
    }


@router.get("/{engagement_id}/testing-coverage")
async def get_engagement_testing_coverage(
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

    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement_id,
    )

    return {
        "engagement": {
            "id": engagement.id,
            "name": engagement.name,
        },
        "coverage": coverage,
    }
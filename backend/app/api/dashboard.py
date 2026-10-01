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
    tags=["Dashboard"],
)


@router.get("/{engagement_id}/dashboard")
async def get_engagement_dashboard(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    # ---------------------------------------------------------
    # Engagement
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Assets
    # ---------------------------------------------------------
    result = await db.execute(
        select(Asset).where(
            Asset.engagement_id == engagement_id
        )
    )

    assets = result.scalars().all()

    # ---------------------------------------------------------
    # Scope
    # ---------------------------------------------------------
    result = await db.execute(
        select(Scope).where(
            Scope.engagement_id == engagement_id
        )
    )

    scopes = result.scalars().all()

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

    # ---------------------------------------------------------
    # Services
    # ---------------------------------------------------------
    result = await db.execute(
        select(Service).where(
            Service.engagement_id == engagement_id
        )
    )

    services = result.scalars().all()

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
        if service.service.lower()
        in {"https", "ssl/http", "ssl/https"}
    ]

    # ---------------------------------------------------------
    # Activities
    # ---------------------------------------------------------
    result = await db.execute(
        select(Activity).where(
            Activity.engagement_id == engagement_id
        )
    )

    activities = result.scalars().all()

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------
    result = await db.execute(
        select(Evidence).where(
            Evidence.engagement_id == engagement_id
        )
    )

    evidence = result.scalars().all()

    # ---------------------------------------------------------
    # Findings
    # ---------------------------------------------------------
    result = await db.execute(
        select(Finding).where(
            Finding.engagement_id == engagement_id
        )
    )

    findings = result.scalars().all()

    validated_findings = [
        finding
        for finding in findings
        if finding.validation_status == "validated"
    ]

    open_findings = [
        finding
        for finding in findings
        if finding.status == "open"
    ]

    closed_findings = [
        finding
        for finding in findings
        if finding.status == "closed"
    ]

    # ---------------------------------------------------------
    # Testing Coverage
    # ---------------------------------------------------------
    coverage = await get_testing_coverage(
        db,
        engagement_id=engagement_id,
    )

    tested_count = 0
    untested_count = 0

    for area in coverage.values():
        for status in area.values():
            if status == "tested":
                tested_count += 1
            else:
                untested_count += 1

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------
    return {
        "engagement": {
            "id": engagement.id,
            "name": engagement.name,
            "client": engagement.client,
            "status": engagement.status,
            "description": engagement.description,
            "created_at": engagement.created_at,
        },
        "assets": {
            "total": len(assets),
            "in_scope": len(in_scope_assets),
            "excluded": len(excluded_assets),
        },
        "services": {
            "total": len(services),
            "in_scope": len(in_scope_services),
            "open": len(open_services),
            "http": len(http_services),
            "https": len(https_services),
        },
        "testing": {
            "tested": tested_count,
            "untested": untested_count,
            "coverage": coverage,
        },
        "findings": {
            "total": len(findings),
            "validated": len(validated_findings),
            "open": len(open_findings),
            "closed": len(closed_findings),
        },
        "activities": len(activities),
        "evidence_items": len(evidence),
    }
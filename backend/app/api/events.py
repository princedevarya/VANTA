import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.models.asset_relationship import AssetRelationship
from app.models.technology import Technology
from app.schemas.event import ToolEventCreate

from app.services.adapters.registry import get_adapter
from app.services.event_engine import process_tool_result
from app.services.parsers.nmap import parse_nmap_output
from app.services.service_inventory import store_discovered_services
from app.services.target_resolver import resolve_asset_target


router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)


SUPPORTED_NETWORK_TESTS = {
    "port_enumeration",
    "service_enumeration",
    "network_configuration",
}


SUPPORTED_RECON_TESTS = {
    "dns",
    "subdomain_discovery",
    "technology_discovery",
}


SUPPORTED_WEB_TESTS = {
    "authentication",
    "authorization",
    "session_management",
    "input_validation",
    "business_logic",
}


SUPPORTED_API_TESTS = {
    "authentication",
    "authorization",
    "object_level_authorization",
    "rate_limiting",
    "input_validation",
}


def parse_mock_subdomains(output: str) -> list[str]:
    discovered = []

    for line in output.splitlines():
        match = re.match(
            r"^SUBDOMAIN\s+(.+)$",
            line.strip(),
        )

        if match:
            value = match.group(1).strip()

            if value and value not in discovered:
                discovered.append(value)

    return discovered


def parse_mock_technologies(
    output: str,
) -> list[dict[str, str]]:
    discovered = []

    for line in output.splitlines():
        match = re.match(
            r"^TECHNOLOGY\s+(\S+)\s+(\S+)$",
            line.strip(),
        )

        if match:
            name = match.group(1).strip()
            category = match.group(2).strip()

            if name and category:
                technology = {
                    "name": name,
                    "category": category,
                }

                if technology not in discovered:
                    discovered.append(technology)

    return discovered


async def store_discovered_subdomains(
    db: AsyncSession,
    *,
    engagement_id: str,
    parent_asset_id: str,
    subdomains: list[str],
):
    discovered_assets = []

    parent_result = await db.execute(
        select(Asset).where(
            Asset.id == parent_asset_id,
            Asset.engagement_id == engagement_id,
        )
    )

    parent_asset = parent_result.scalar_one_or_none()

    if parent_asset is None:
        raise ValueError(
            "Parent asset not found in this engagement"
        )

    for subdomain in subdomains:
        result = await db.execute(
            select(Asset).where(
                Asset.engagement_id == engagement_id,
                Asset.value == subdomain,
            )
        )

        asset = result.scalar_one_or_none()

        if asset is None:
            asset = Asset(
                engagement_id=engagement_id,
                value=subdomain,
                asset_type="subdomain",
                status="discovered",
                description="Discovered during subdomain reconnaissance",
            )

            db.add(asset)
            await db.flush()

        relationship_result = await db.execute(
            select(AssetRelationship).where(
                AssetRelationship.engagement_id == engagement_id,
                AssetRelationship.source_asset_id == parent_asset_id,
                AssetRelationship.target_asset_id == asset.id,
            )
        )

        relationship = relationship_result.scalar_one_or_none()

        if relationship is None and asset.id != parent_asset_id:
            db.add(
                AssetRelationship(
                    engagement_id=engagement_id,
                    source_asset_id=parent_asset_id,
                    target_asset_id=asset.id,
                    relationship_type="discovered_from",
                    description=(
                        "Subdomain discovered from parent domain "
                        "during reconnaissance"
                    ),
                )
            )

        discovered_assets.append(asset)

    await db.commit()

    for asset in discovered_assets:
        await db.refresh(asset)

    return discovered_assets


async def store_discovered_technologies(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str,
    activity_id: str,
    evidence_id: str,
    technologies: list[dict[str, str]],
):
    discovered_technologies = []

    asset_result = await db.execute(
        select(Asset).where(
            Asset.id == asset_id,
            Asset.engagement_id == engagement_id,
        )
    )

    asset = asset_result.scalar_one_or_none()

    if asset is None:
        raise ValueError(
            "Asset not found in this engagement"
        )

    for technology_data in technologies:
        name = technology_data["name"]
        category = technology_data["category"]

        result = await db.execute(
            select(Technology).where(
                Technology.engagement_id == engagement_id,
                Technology.asset_id == asset_id,
                Technology.name == name,
                Technology.category == category,
            )
        )

        technology = result.scalar_one_or_none()

        if technology is None:
            technology = Technology(
                engagement_id=engagement_id,
                asset_id=asset_id,
                name=name,
                category=category,
                source_activity_id=activity_id,
                source_evidence_id=evidence_id,
            )

            db.add(technology)
            await db.flush()

        else:
            technology.source_activity_id = activity_id
            technology.source_evidence_id = evidence_id

        discovered_technologies.append(technology)

    await db.commit()

    for technology in discovered_technologies:
        await db.refresh(technology)

    return discovered_technologies


@router.post("/tool")
async def create_tool_event(
    event: ToolEventCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        target = await resolve_asset_target(
            db,
            engagement_id=event.engagement_id,
            asset_id=event.asset_id,
        )

        testing_area = event.testing_area
        test_type = event.test_type

        if event.tool == "nmap":
            testing_area = testing_area or "network"
            test_type = test_type or "service_enumeration"

            if testing_area != "network":
                raise ValueError(
                    "nmap currently supports network testing only"
                )

            if test_type not in {
                "port_enumeration",
                "service_enumeration",
            }:
                raise ValueError(
                    f"nmap does not support testing type: {test_type}"
                )

        elif event.tool == "mock":
            testing_area = testing_area or "network"
            test_type = test_type or "service_enumeration"

            if testing_area == "network":
                if test_type not in SUPPORTED_NETWORK_TESTS:
                    raise ValueError(
                        f"mock does not support network testing type: {test_type}"
                    )

            elif testing_area == "recon":
                if test_type not in SUPPORTED_RECON_TESTS:
                    raise ValueError(
                        f"mock does not support recon testing type: {test_type}"
                    )

            elif testing_area == "web":
                if test_type not in SUPPORTED_WEB_TESTS:
                    raise ValueError(
                        f"mock does not support web testing type: {test_type}"
                    )

            elif testing_area == "api":
                if test_type not in SUPPORTED_API_TESTS:
                    raise ValueError(
                        f"mock does not support api testing type: {test_type}"
                    )

            else:
                raise ValueError(
                    "mock currently supports recon, network, web, and api testing only"
                )

        adapter = get_adapter(event.tool)

        result = await adapter.run(
            target,
            test_type=test_type or "service_enumeration",
        )

        discovered_services = []
        discovered_assets = []
        discovered_technologies = []

        if (
            result.tool in {"nmap", "mock"}
            and result.return_code == 0
            and testing_area == "network"
        ):
            parsed_result = parse_nmap_output(result.output)

            discovered_services = await store_discovered_services(
                db,
                engagement_id=event.engagement_id,
                asset_id=event.asset_id,
                parsed_result=parsed_result,
            )

        if (
            result.tool == "mock"
            and result.return_code == 0
            and testing_area == "recon"
            and test_type == "subdomain_discovery"
            and event.asset_id
        ):
            subdomains = parse_mock_subdomains(
                result.output
            )

            discovered_assets = (
                await store_discovered_subdomains(
                    db,
                    engagement_id=event.engagement_id,
                    parent_asset_id=event.asset_id,
                    subdomains=subdomains,
                )
            )

        processed = await process_tool_result(
            db,
            engagement_id=event.engagement_id,
            asset_id=event.asset_id,
            result=result,
            title=event.title,
            testing_area=testing_area,
            test_type=test_type,
        )

        if (
            result.tool == "mock"
            and result.return_code == 0
            and testing_area == "recon"
            and test_type == "technology_discovery"
            and event.asset_id
        ):
            technologies = parse_mock_technologies(
                result.output
            )

            discovered_technologies = (
                await store_discovered_technologies(
                    db,
                    engagement_id=event.engagement_id,
                    asset_id=event.asset_id,
                    activity_id=processed["activity"].id,
                    evidence_id=processed["evidence"].id,
                    technologies=technologies,
                )
            )

        return {
            "tool": result.tool,
            "target": target,
            "return_code": result.return_code,
            "activity_id": processed["activity"].id,
            "evidence_id": processed["evidence"].id,
            "testing_area": testing_area,
            "test_type": test_type,
            "discovered_services": [
                {
                    "id": service.id,
                    "port": service.port,
                    "protocol": service.protocol,
                    "state": service.state,
                    "service": service.service,
                }
                for service in discovered_services
            ],
            "discovered_assets": [
                {
                    "id": asset.id,
                    "value": asset.value,
                    "asset_type": asset.asset_type,
                    "status": asset.status,
                    "description": asset.description,
                }
                for asset in discovered_assets
            ],
            "discovered_technologies": [
                {
                    "id": technology.id,
                    "asset_id": technology.asset_id,
                    "name": technology.name,
                    "category": technology.category,
                    "version": technology.version,
                    "source_activity_id": technology.source_activity_id,
                    "source_evidence_id": technology.source_evidence_id,
                }
                for technology in discovered_technologies
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
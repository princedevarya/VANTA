from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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

        adapter = get_adapter(event.tool)
        result = await adapter.run(target)

        parsed_result = None
        discovered_services = []

        # Both the real Nmap adapter and the mock adapter produce
        # Nmap-compatible service output. Parse both through the same
        # inventory pipeline so the mock is useful for end-to-end testing.
        if result.tool in {"nmap", "mock"} and result.return_code == 0:
            parsed_result = parse_nmap_output(result.output)
            discovered_services = await store_discovered_services(
                db,
                engagement_id=event.engagement_id,
                asset_id=event.asset_id,
                parsed_result=parsed_result,
            )

        testing_area = None
        test_type = None

        if result.tool in {"nmap", "mock"}:
            testing_area = "network"
            test_type = "service_enumeration"

        processed = await process_tool_result(
            db,
            engagement_id=event.engagement_id,
            asset_id=event.asset_id,
            result=result,
            title=event.title,
            testing_area=testing_area,
            test_type=test_type,
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
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
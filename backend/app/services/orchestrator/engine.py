from sqlalchemy.ext.asyncio import AsyncSession

from app.services.adapters.registry import get_adapter
from app.services.asset_discovery import (
    get_or_create_discovery_seed,
    store_discovered_subdomains,
)
from app.services.endpoint_inventory import store_discovered_endpoints
from app.services.event_engine import process_tool_result
from app.services.parsers.registry import get_parser
from app.services.target_resolver import (
    resolve_asset_target,
    resolve_discovery_target,
)


KATANA_RESPONSE_ENDPOINT_LIMIT = 100


async def execute_tool(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str | None,
    target: str | None,
    tool: str,
    title: str,
    execution_mode: str,
    testing_area: str | None,
    test_type: str | None,
) -> dict:
    """
    Execute a VANTA tool through the adapter/orchestrator pipeline.

    Discovery mode:
        target -> scope validation -> discovery seed Asset -> tool

    Testing mode:
        asset_id -> scope validation -> Asset -> tool

    Katana:
        tool output -> parser -> endpoint inventory
        while keeping the API response bounded.
    """

    # ---------------------------------------------------------
    # Resolve execution target
    # ---------------------------------------------------------

    if execution_mode == "discovery":
        if not target:
            raise ValueError(
                "Discovery execution requires a target"
            )

        execution_target = await resolve_discovery_target(
            db,
            engagement_id=engagement_id,
            target=target,
        )

        discovery_seed = await get_or_create_discovery_seed(
            db,
            engagement_id=engagement_id,
            target=execution_target,
        )

        resolved_asset_id = discovery_seed.id

    elif execution_mode == "testing":
        if not asset_id:
            raise ValueError(
                "Testing execution requires an asset_id"
            )

        execution_target = await resolve_asset_target(
            db,
            engagement_id=engagement_id,
            asset_id=asset_id,
        )

        resolved_asset_id = asset_id

    else:
        raise ValueError(
            f"Unsupported execution mode: {execution_mode}"
        )

    # ---------------------------------------------------------
    # Execute adapter
    # ---------------------------------------------------------

    adapter = get_adapter(tool)

    result = await adapter.run(
        execution_target,
        test_type=test_type,
    )

    # ---------------------------------------------------------
    # Parse tool output
    # ---------------------------------------------------------

    parsed: dict = {}

    parser = get_parser(tool)

    if parser is not None and result.return_code == 0:
        parsed = parser(result.output)

    # ---------------------------------------------------------
    # Discovery asset handling
    # ---------------------------------------------------------

    discovered_assets = []

    if (
        tool == "subfinder"
        and execution_mode == "discovery"
        and result.return_code == 0
        and test_type == "subdomain_discovery"
    ):
        discovered_assets = await store_discovered_subdomains(
            db,
            engagement_id=engagement_id,
            parent_asset_id=resolved_asset_id,
            subdomains=parsed.get("subdomains", []),
        )

    # ---------------------------------------------------------
    # HTTP service handling
    # ---------------------------------------------------------

    http_services = []

    if (
        tool == "httpx"
        and result.return_code == 0
        and test_type == "technology_discovery"
    ):
        http_services = parsed.get(
            "http_services",
            [],
        )

    # ---------------------------------------------------------
    # Katana endpoint inventory
    # ---------------------------------------------------------

    katana_endpoint_count = 0
    katana_endpoint_preview: list[dict] = []
    stored_endpoint_count = 0

    if (
        tool == "katana"
        and result.return_code == 0
        and resolved_asset_id
    ):
        katana_endpoints = parsed.get(
            "endpoints",
            [],
        )

        katana_endpoint_count = parsed.get(
            "endpoint_count",
            len(katana_endpoints),
        )

        # Persist ALL parsed endpoints into the VANTA endpoint
        # inventory. The inventory layer handles deduplication.
        if katana_endpoints:
            stored_endpoints = await store_discovered_endpoints(
                db,
                engagement_id=engagement_id,
                asset_id=resolved_asset_id,
                parsed_result={
                    "endpoints": katana_endpoints,
                },
            )

            stored_endpoint_count = len(stored_endpoints)

        # Never return the complete endpoint inventory through
        # the API response. Keep the response bounded.
        katana_endpoint_preview = katana_endpoints[
            :KATANA_RESPONSE_ENDPOINT_LIMIT
        ]

    # ---------------------------------------------------------
    # Activity + evidence + findings
    # ---------------------------------------------------------

    processed = await process_tool_result(
        db,
        engagement_id=engagement_id,
        asset_id=resolved_asset_id,
        title=title,
        testing_area=testing_area,
        test_type=test_type,
        result=result,
    )

    # ---------------------------------------------------------
    # API response
    # ---------------------------------------------------------

    return {
        "tool": result.tool,
        "target": execution_target,
        "command": result.command,
        "return_code": result.return_code,

        # Katana raw output is intentionally not returned because
        # it can be very large.
        "output": (
            result.output
            if tool != "katana"
            else None
        ),

        "metadata": result.metadata,

        "activity": processed["activity"],
        "evidence": processed["evidence"],
        "findings": processed["findings"],

        "parsed": (
            {
                **parsed,
                "endpoints": katana_endpoint_preview,
            }
            if tool == "katana"
            else parsed
        ),

        "http_services": http_services,
        "discovered_assets": discovered_assets,

        "asset_id": resolved_asset_id,
        "execution_mode": execution_mode,
        "testing_area": testing_area,
        "test_type": test_type,

        # Katana inventory information.
        "endpoint_count": katana_endpoint_count,
        "stored_endpoint_count": stored_endpoint_count,
        "endpoint_preview_count": len(
            katana_endpoint_preview
        ),
    }

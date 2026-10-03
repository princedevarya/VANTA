from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Endpoint


async def store_discovered_endpoints(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str,
    parsed_result: dict,
    activity_id: str | None = None,
    evidence_id: str | None = None,
) -> list[Endpoint]:
    """
    Store normalized discovered endpoints in the VANTA inventory.

    Deduplication key:

        engagement_id
        asset_id
        method
        url

    Existing endpoints are updated with the newest observed
    metadata. New endpoints are inserted.

    The function intentionally performs one initial lookup rather
    than one SELECT query per endpoint.
    """

    items = parsed_result.get(
        "endpoints",
        [],
    )

    if not items:
        return []

    # ---------------------------------------------------------
    # Normalize incoming records first
    # ---------------------------------------------------------

    normalized_items: list[dict] = []

    incoming_keys: set[tuple[str, str]] = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        url = item.get("url")

        if not isinstance(url, str):
            continue

        url = url.strip()

        if not url:
            continue

        method = item.get(
            "method",
            "GET",
        )

        method = str(method).upper().strip()

        if not method:
            method = "GET"

        key = (
            method,
            url,
        )

        # Deduplicate the current crawl before touching DB.
        if key in incoming_keys:
            continue

        incoming_keys.add(key)

        normalized_items.append(
            {
                **item,
                "url": url,
                "method": method,
            }
        )

    if not normalized_items:
        return []

    # ---------------------------------------------------------
    # Load existing endpoints for this engagement + asset
    # ---------------------------------------------------------

    result = await db.execute(
        select(Endpoint).where(
            Endpoint.engagement_id == engagement_id,
            Endpoint.asset_id == asset_id,
        )
    )

    existing_endpoints = result.scalars().all()

    existing_by_key: dict[
        tuple[str, str],
        Endpoint,
    ] = {
        (
            endpoint.method.upper(),
            endpoint.url,
        ): endpoint
        for endpoint in existing_endpoints
    }

    stored_endpoints: list[Endpoint] = []

    # ---------------------------------------------------------
    # Insert / update inventory
    # ---------------------------------------------------------

    for item in normalized_items:
        url = item["url"]
        method = item["method"]

        key = (
            method,
            url,
        )

        port = item.get("port")

        try:
            port = (
                int(port)
                if port is not None
                else None
            )
        except (TypeError, ValueError):
            port = None

        status_code = item.get(
            "status_code"
        )

        try:
            status_code = (
                int(status_code)
                if status_code is not None
                else None
            )
        except (TypeError, ValueError):
            status_code = None

        endpoint = existing_by_key.get(key)

        if endpoint is None:
            endpoint = Endpoint(
                engagement_id=engagement_id,
                asset_id=asset_id,

                url=url,
                method=method,

                scheme=item.get("scheme"),
                host=item.get("host"),
                port=port,

                path=item.get("path"),
                query=item.get("query"),

                status_code=status_code,

                content_type=item.get(
                    "content_type"
                ),

                server=item.get(
                    "server"
                ),

                source_url=item.get(
                    "source_url"
                ),

                tag=item.get(
                    "tag"
                ),

                attribute=item.get(
                    "attribute"
                ),

                source_activity_id=activity_id,
                source_evidence_id=evidence_id,
            )

            db.add(endpoint)

            # Important:
            # Add the object to the lookup map immediately so
            # duplicates cannot create another object during the
            # same execution.
            existing_by_key[key] = endpoint

        else:
            # Refresh existing endpoint metadata from the newest
            # observation.

            endpoint.scheme = item.get(
                "scheme"
            )

            endpoint.host = item.get(
                "host"
            )

            endpoint.port = port

            endpoint.path = item.get(
                "path"
            )

            endpoint.query = item.get(
                "query"
            )

            endpoint.status_code = status_code

            endpoint.content_type = item.get(
                "content_type"
            )

            endpoint.server = item.get(
                "server"
            )

            endpoint.source_url = item.get(
                "source_url"
            )

            endpoint.tag = item.get(
                "tag"
            )

            endpoint.attribute = item.get(
                "attribute"
            )

            endpoint.source_activity_id = (
                activity_id
            )

            endpoint.source_evidence_id = (
                evidence_id
            )

        stored_endpoints.append(endpoint)

    # ---------------------------------------------------------
    # Commit once
    # ---------------------------------------------------------

    await db.commit()

    # Flush/refresh objects so generated IDs are available.
    for endpoint in stored_endpoints:
        if endpoint.id is None:
            await db.refresh(endpoint)

    return stored_endpoints

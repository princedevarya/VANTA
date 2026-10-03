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
    stored_endpoints: list[Endpoint] = []

    for item in parsed_result.get("endpoints", []):
        url = item.get("url")

        if not url:
            continue

        method = item.get("method") or "GET"
        method = str(method).upper()

        port = item.get("port")
        status_code = item.get("status_code")

        try:
            port = int(port) if port is not None else None
        except (TypeError, ValueError):
            port = None

        try:
            status_code = (
                int(status_code)
                if status_code is not None
                else None
            )
        except (TypeError, ValueError):
            status_code = None

        result = await db.execute(
            select(Endpoint).where(
                Endpoint.engagement_id == engagement_id,
                Endpoint.asset_id == asset_id,
                Endpoint.method == method,
                Endpoint.url == url,
            )
        )

        endpoint = result.scalar_one_or_none()

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
                content_type=item.get("content_type"),
                server=item.get("server"),
                source_url=item.get("source_url"),
                tag=item.get("tag"),
                attribute=item.get("attribute"),
                source_activity_id=activity_id,
                source_evidence_id=evidence_id,
            )

            db.add(endpoint)

        else:
            endpoint.scheme = item.get("scheme")
            endpoint.host = item.get("host")
            endpoint.port = port
            endpoint.path = item.get("path")
            endpoint.query = item.get("query")
            endpoint.status_code = status_code
            endpoint.content_type = item.get("content_type")
            endpoint.server = item.get("server")
            endpoint.source_url = item.get("source_url")
            endpoint.tag = item.get("tag")
            endpoint.attribute = item.get("attribute")
            endpoint.source_activity_id = activity_id
            endpoint.source_evidence_id = evidence_id

        stored_endpoints.append(endpoint)

    await db.commit()

    for endpoint in stored_endpoints:
        await db.refresh(endpoint)

    return stored_endpoints

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HttpService


async def store_discovered_http_services(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str,
    parsed_result: dict,
    activity_id: str | None = None,
    evidence_id: str | None = None,
) -> list[HttpService]:
    stored_services: list[HttpService] = []

    for item in parsed_result.get("http_services", []):
        url = item.get("url")

        if not url:
            continue

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
            select(HttpService).where(
                HttpService.engagement_id == engagement_id,
                HttpService.asset_id == asset_id,
                HttpService.url == url,
            )
        )

        service = result.scalar_one_or_none()

        if service is None:
            service = HttpService(
                engagement_id=engagement_id,
                asset_id=asset_id,
                url=url,
                scheme=item.get("scheme"),
                host=item.get("host"),
                port=port,
                status_code=status_code,
                title=item.get("title"),
                webserver=item.get("webserver"),
                source_activity_id=activity_id,
                source_evidence_id=evidence_id,
            )

            db.add(service)

        else:
            service.scheme = item.get("scheme")
            service.host = item.get("host")
            service.port = port
            service.status_code = status_code
            service.title = item.get("title")
            service.webserver = item.get("webserver")
            service.source_activity_id = activity_id
            service.source_evidence_id = evidence_id

        stored_services.append(service)

    await db.commit()

    for service in stored_services:
        await db.refresh(service)

    return stored_services
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Service


async def store_discovered_services(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str,
    parsed_result: dict,
) -> list[Service]:

    stored_services = []

    for item in parsed_result["services"]:
        existing = await db.execute(
            select(Service).where(
                Service.engagement_id == engagement_id,
                Service.asset_id == asset_id,
                Service.port == item["port"],
                Service.protocol == item["protocol"],
            )
        )

        service = existing.scalar_one_or_none()

        if service is None:
            service = Service(
                engagement_id=engagement_id,
                asset_id=asset_id,
                port=item["port"],
                protocol=item["protocol"],
                state=item["state"],
                service=item["service"],
            )

            db.add(service)
            stored_services.append(service)

        else:
            service.state = item["state"]
            service.service = item["service"]
            stored_services.append(service)

    await db.commit()

    for service in stored_services:
        await db.refresh(service)

    return stored_services
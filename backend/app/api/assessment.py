from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.models.engagement import Engagement
from app.models.scope import Scope

router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["Assessment"],
)


class AssessmentStartRequest(BaseModel):
    target: str = Field(min_length=1, max_length=2048)


def valid_hostname(host: str) -> bool:
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-.")
    if any(ch not in allowed for ch in host):
        return False

    if host.startswith("-") or host.endswith("-") or ".." in host:
        return False

    return all(
        label
        and not label.startswith("-")
        and not label.endswith("-")
        for label in host.split(".")
    )


def normalize_target(raw_target: str) -> tuple[str, str, str | None]:
    raw = raw_target.strip()

    if not raw:
        raise ValueError("Target is required")

    parsed = urlsplit(
        raw if "://" in raw else f"//{raw}"
    )

    if parsed.username or parsed.password:
        raise ValueError(
            "Targets containing credentials are not allowed"
        )

    host = parsed.hostname
    scheme = (
        parsed.scheme
        if parsed.scheme in {"http", "https"}
        else None
    )

    if not host:
        raise ValueError(
            "Enter a valid domain, IP address, or URL"
        )

    host = host.rstrip(".").lower()

    try:
        ipaddress.ip_address(host)
        target_type = "ip"

    except ValueError:
        if host != "localhost" and "." not in host:
            raise ValueError(
                "Enter a valid domain, IP address, or URL"
            )

        if len(host) > 253 or not valid_hostname(host):
            raise ValueError("Target hostname is invalid")

        target_type = "domain"

    return host, target_type, scheme


async def delete_engagement_data(
    db: AsyncSession,
    engagement_id: str,
) -> None:

    statements = [
        """
        DELETE FROM finding_evidence
        WHERE finding_id IN (
            SELECT id
            FROM findings
            WHERE engagement_id = :engagement_id
        )
        """,

        """
        DELETE FROM attack_path_steps
        WHERE attack_path_id IN (
            SELECT id
            FROM attack_paths
            WHERE engagement_id = :engagement_id
        )
        """,

        "DELETE FROM endpoints WHERE engagement_id = :engagement_id",

        "DELETE FROM http_services WHERE engagement_id = :engagement_id",

        "DELETE FROM services WHERE engagement_id = :engagement_id",

        "DELETE FROM asset_relationships WHERE engagement_id = :engagement_id",

        "DELETE FROM technologies WHERE engagement_id = :engagement_id",

        "DELETE FROM findings WHERE engagement_id = :engagement_id",

        "DELETE FROM evidence WHERE engagement_id = :engagement_id",

        "DELETE FROM activities WHERE engagement_id = :engagement_id",

        "DELETE FROM attack_paths WHERE engagement_id = :engagement_id",

        "DELETE FROM scopes WHERE engagement_id = :engagement_id",

        "DELETE FROM assets WHERE engagement_id = :engagement_id",

        "DELETE FROM engagements WHERE id = :engagement_id",
    ]

    for statement in statements:
        await db.execute(
            text(statement),
            {"engagement_id": engagement_id},
        )


@router.post("/start")
async def start_assessment(
    data: AssessmentStartRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        target, target_type, scheme = normalize_target(
            data.target
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    await db.execute(
        text("PRAGMA foreign_keys=ON")
    )

    previous = (
        await db.execute(
            text(
                """
                SELECT id
                FROM engagements
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
        )
    ).scalar_one_or_none()

    if previous:
        await delete_engagement_data(
            db,
            previous,
        )

    engagement = Engagement(
        name=f"Assessment — {target}",
        client=None,
        description=(
            f"Target-first security assessment for {target}"
            + (
                f" ({scheme})"
                if scheme
                else ""
            )
        ),
    )

    db.add(engagement)
    await db.flush()

    scope = Scope(
        engagement_id=engagement.id,
        target=target,
        target_type=target_type,
        scope_type="include",
        description="Primary assessment target",
    )

    asset = Asset(
        engagement_id=engagement.id,
        value=target,
        asset_type=target_type,
        status="active",
        description="Primary assessment target",
    )

    db.add(scope)
    db.add(asset)

    await db.commit()

    await db.refresh(engagement)
    await db.refresh(scope)
    await db.refresh(asset)

    return {
        "target": target,
        "target_type": target_type,
        "scheme": scheme,
        "engagement": engagement,
        "scope": scope,
        "asset": asset,
    }

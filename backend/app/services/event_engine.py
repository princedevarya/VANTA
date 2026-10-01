from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Evidence
from app.services.adapters.base import ToolResult


async def process_tool_result(
    db: AsyncSession,
    *,
    engagement_id: str,
    asset_id: str | None,
    result: ToolResult,
    title: str,
    testing_area: str | None = None,
    test_type: str | None = None,
):
    activity = Activity(
        engagement_id=engagement_id,
        asset_id=asset_id,
        activity_type="tool_execution",
        testing_area=testing_area,
        test_type=test_type,
        title=title,
        description=f"Execution of {result.tool}",
        command=result.command,
        tool=result.tool,
        status="completed" if result.return_code == 0 else "failed",
    )

    db.add(activity)
    await db.flush()

    evidence = Evidence(
        engagement_id=engagement_id,
        activity_id=activity.id,
        asset_id=asset_id,
        evidence_type="command_output",
        title=f"{result.tool} output",
        content=result.output,
    )

    db.add(evidence)

    await db.commit()

    await db.refresh(activity)
    await db.refresh(evidence)

    return {
        "activity": activity,
        "evidence": evidence,
    }
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.report_generator import generate_report


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Reports"],
)


@router.get("/{engagement_id}/report")
async def generate_engagement_report(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        filename, report_path = await generate_report(
            db,
            engagement_id=engagement_id,
        )

        return FileResponse(
            path=report_path,
            media_type="text/markdown",
            filename=filename,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
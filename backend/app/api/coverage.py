from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.coverage import TESTING_TAXONOMY
from app.services.coverage_traceability import (
    get_coverage_traceability,
)


router = APIRouter(
    prefix="/api/v1/engagements",
    tags=["Coverage"],
)


@router.get(
    "/{engagement_id}/coverage/{testing_area}/{test_type}",
)
async def get_coverage_item_traceability(
    engagement_id: str,
    testing_area: str,
    test_type: str,
    db: AsyncSession = Depends(get_db),
):
    allowed_test_types = TESTING_TAXONOMY.get(
        testing_area,
        [],
    )

    if test_type not in allowed_test_types:
        raise HTTPException(
            status_code=404,
            detail="Unknown coverage item",
        )

    return await get_coverage_traceability(
        db,
        engagement_id=engagement_id,
        testing_area=testing_area,
        test_type=test_type,
    )
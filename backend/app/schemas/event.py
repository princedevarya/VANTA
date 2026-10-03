from typing import Literal

from pydantic import BaseModel


class ToolEventCreate(BaseModel):
    engagement_id: str
    asset_id: str | None = None
    target: str | None = None
    tool: str
    title: str
    execution_mode: Literal["discovery", "testing"] = "testing"
    testing_area: str | None = None
    test_type: str | None = None
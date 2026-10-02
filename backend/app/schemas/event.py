from pydantic import BaseModel


class ToolEventCreate(BaseModel):
    engagement_id: str
    asset_id: str | None = None
    tool: str
    title: str
    testing_area: str | None = None
    test_type: str | None = None
from pydantic import BaseModel


class ToolEventCreate(BaseModel):
    engagement_id: str
    asset_id: str | None = None
    tool: str
    title: str
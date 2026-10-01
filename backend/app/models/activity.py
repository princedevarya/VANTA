from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    engagement_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("engagements.id", ondelete="CASCADE"),
        nullable=False,
    )

    asset_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )

    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Security testing classification
    testing_area: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    test_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    command: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tool: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
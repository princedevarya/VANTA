from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

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

    activity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("activities.id", ondelete="SET NULL"),
        nullable=True,
    )

    asset_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
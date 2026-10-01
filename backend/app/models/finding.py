from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Finding(Base):
    __tablename__ = "findings"

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

    activity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("activities.id", ondelete="SET NULL"),
        nullable=True,
    )

    evidence_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("evidence.id", ondelete="SET NULL"),
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

    severity: Mapped[str] = mapped_column(
        String(20),
        default="informational",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
    )

    validation_status: Mapped[str] = mapped_column(
        String(30),
        default="hypothesis",
    )

    remediation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    retest_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    retest_activity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("activities.id", ondelete="SET NULL"),
        nullable=True,
    )

    retest_evidence_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("evidence.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
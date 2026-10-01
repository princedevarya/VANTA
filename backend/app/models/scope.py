from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Scope(Base):
    __tablename__ = "scopes"

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

    target: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    target_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    scope_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="include",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

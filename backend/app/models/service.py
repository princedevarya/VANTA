from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

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

    asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )

    port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    protocol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssetRelationship(Base):
    __tablename__ = "asset_relationships"

    __table_args__ = (
        UniqueConstraint(
            "engagement_id",
            "source_asset_id",
            "target_asset_id",
            "relationship_type",
            name="uq_asset_relationship",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    engagement_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "engagements.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    source_asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    target_asset_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
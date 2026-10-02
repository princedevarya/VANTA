from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AttackPathStep(Base):
    __tablename__ = "attack_path_steps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    attack_path_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "attack_paths.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    step_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    asset_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "assets.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    activity_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "activities.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    evidence_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "evidence.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    finding_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "findings.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    attack_path: Mapped["AttackPath"] = relationship(
        "AttackPath",
        back_populates="steps",
    )
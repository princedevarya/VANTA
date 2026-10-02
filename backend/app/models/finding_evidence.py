from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FindingEvidence(Base):
    __tablename__ = "finding_evidence"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    finding_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
    )

    evidence_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50),
        default="supporting",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
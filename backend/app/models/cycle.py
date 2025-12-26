"""Cycle ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class Cycle(Base):
    """Cycle model - represents structured data collection cycles."""

    __tablename__ = "cycles"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    cycle_name = Column(String(50), nullable=False)
    cycle_number = Column(Integer, nullable=False, index=True)
    s3_prefix = Column(String(100), nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)
    description = Column(Text)
    cycle_metadata = Column("metadata", JSONB)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="cycles")
    sync_sessions = relationship("SyncSession", back_populates="cycle")

    def __repr__(self) -> str:
        return f"<Cycle(id={self.id}, cycle_name='{self.cycle_name}', project_id={self.project_id}, status='{self.status}')>"

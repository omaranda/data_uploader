"""SyncSession ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class SyncSession(Base):
    """SyncSession model - represents upload sessions."""

    __tablename__ = "sync_sessions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    cycle_id = Column(Integer, ForeignKey("cycles.id", ondelete="SET NULL"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    local_directory = Column(Text, nullable=False)
    s3_prefix = Column(String(50), nullable=False)
    aws_profile = Column(String(100), nullable=False)
    max_workers = Column(Integer, default=15)
    times_to_retry = Column(Integer, default=3)
    use_find = Column(Boolean, default=True)
    status = Column(String(50), default="in_progress", index=True)
    total_files = Column(Integer, default=0)
    total_size_bytes = Column(BigInteger, default=0)
    files_uploaded = Column(Integer, default=0)
    files_failed = Column(Integer, default=0)
    files_skipped = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    project = relationship("Project", back_populates="sync_sessions")
    cycle = relationship("Cycle", back_populates="sync_sessions")
    user = relationship("User", back_populates="sync_sessions")
    file_uploads = relationship("FileUpload", back_populates="sync_session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SyncSession(id={self.id}, project_id={self.project_id}, status='{self.status}')>"

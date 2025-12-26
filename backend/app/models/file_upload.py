"""FileUpload ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class FileUpload(Base):
    """FileUpload model - represents individual file upload records."""

    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sync_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    local_path = Column(Text, nullable=False)
    s3_key = Column(Text, nullable=False, index=True)
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    status = Column(String(20), default="pending", index=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    uploaded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sync_session = relationship("SyncSession", back_populates="file_uploads")

    def __repr__(self) -> str:
        return f"<FileUpload(id={self.id}, session_id={self.session_id}, s3_key='{self.s3_key}', status='{self.status}')>"

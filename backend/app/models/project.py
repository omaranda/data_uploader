"""Project ORM model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Project(Base):
    """Project model - represents S3 upload projects."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name = Column(String(255), unique=True, nullable=False, index=True)
    bucket_name = Column(String(255), nullable=False)
    aws_region = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="projects")
    cycles = relationship("Cycle", back_populates="project", cascade="all, delete-orphan")
    sync_sessions = relationship("SyncSession", back_populates="project")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, project_name='{self.project_name}', company_id={self.company_id})>"

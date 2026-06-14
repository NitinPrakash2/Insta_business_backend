from sqlalchemy import (
    Column, String, Text, ForeignKey, JSON, Index, UniqueConstraint, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
from src.db_config import Base
import uuid


class Instance(Base):
    __tablename__ = "instance"

    __table_args__ = (
        Index("ix_instance_name_project_id", "name", "project_id"),
        Index("ix_instance_user_id_project_id", "user_id", "project_id"),
        UniqueConstraint("user_id", "project_id", "name", name="uq_instance_user_project_name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    #utility_id = Column(UUID(as_uuid=True), ForeignKey("utility.id", ondelete="CASCADE"), nullable=False)
    utility_id = Column(Integer, ForeignKey("utility.id", ondelete="CASCADE"), nullable=False)

    config_id = Column(UUID(as_uuid=True), ForeignKey("config.id", ondelete="CASCADE"), nullable=True)

    # relationships
    user = relationship("User", back_populates="instances")
    project = relationship("Project", back_populates="instances")
    utility = relationship("Utility", back_populates="instances")
    config = relationship("Config", back_populates="instances")

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

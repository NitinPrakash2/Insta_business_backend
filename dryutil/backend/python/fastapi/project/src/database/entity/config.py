from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db_config import Base
import uuid


class Config(Base):
    __tablename__ = "config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)

    instances = relationship("Instance", back_populates="config", cascade="all, delete")

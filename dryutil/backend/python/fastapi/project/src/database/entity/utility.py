from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.db_config import Base


class Utility(Base):
    __tablename__ = "utility"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    instances = relationship("Instance", back_populates="utility", cascade="all, delete")

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.session import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    job_name = Column(String, nullable=False)
    instance = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    alert_rules = relationship("AlertRule", back_populates="server", cascade="all, delete-orphan")
    alert_events = relationship("AlertEvent", back_populates="server", cascade="all, delete-orphan")

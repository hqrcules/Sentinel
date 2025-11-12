from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.session import Base


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True, index=True)
    alert_rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # triggered, resolved
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    alert_rule = relationship("AlertRule", back_populates="alert_events")
    server = relationship("Server", back_populates="alert_events")

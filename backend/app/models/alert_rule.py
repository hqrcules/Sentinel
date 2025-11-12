from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String, nullable=False)
    promql = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    comparison = Column(String, nullable=False)  # >, <, >=, <=, ==, !=
    repeat_interval_sec = Column(Integer, default=300)  # 5 minutes
    is_active = Column(Boolean, default=True)
    channel = Column(String, default="telegram")  # notification channel

    # Relationships
    server = relationship("Server", back_populates="alert_rules")
    alert_events = relationship("AlertEvent", back_populates="alert_rule", cascade="all, delete-orphan")

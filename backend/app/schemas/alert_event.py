from pydantic import BaseModel
from datetime import datetime


class AlertEventBase(BaseModel):
    alert_rule_id: int
    server_id: int
    metric_name: str
    value: float
    status: str  # triggered, resolved


class AlertEventCreate(AlertEventBase):
    pass


class AlertEventResponse(AlertEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

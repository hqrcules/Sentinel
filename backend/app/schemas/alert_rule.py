from pydantic import BaseModel
from typing import Optional


class AlertRuleBase(BaseModel):
    name: str
    server_id: int
    metric_name: str
    promql: str
    threshold: float
    comparison: str  # >, <, >=, <=, ==, !=
    repeat_interval_sec: int = 300
    is_active: bool = True
    channel: str = "telegram"


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    metric_name: Optional[str] = None
    promql: Optional[str] = None
    threshold: Optional[float] = None
    comparison: Optional[str] = None
    repeat_interval_sec: Optional[int] = None
    is_active: Optional[bool] = None
    channel: Optional[str] = None


class AlertRuleResponse(AlertRuleBase):
    id: int

    class Config:
        from_attributes = True

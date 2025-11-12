from pydantic import BaseModel
from typing import Dict, Any, Optional


class MetricSummary(BaseModel):
    server_id: int
    server_name: str
    metrics: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

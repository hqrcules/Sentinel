from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....db import get_db
from ....models import Server, User
from ....schemas import MetricSummary
from ....services import get_current_user, prometheus_service

router = APIRouter()


@router.get("/servers/{server_id}/summary", response_model=MetricSummary)
async def get_server_metrics_summary(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get metrics summary for a specific server from Prometheus.
    """
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    if not server.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server is not active"
        )

    # Get metrics from Prometheus
    metrics = await prometheus_service.get_server_metrics(
        job_name=server.job_name,
        instance=server.instance
    )

    return MetricSummary(
        server_id=server.id,
        server_name=server.name,
        metrics=metrics
    )

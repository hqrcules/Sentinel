from fastapi import APIRouter
from datetime import datetime
from ....core import settings
from ....schemas import HealthResponse

router = APIRouter()


@router.get("/liveness", response_model=HealthResponse)
async def liveness():
    """
    Simple liveness check endpoint.
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat()
    )

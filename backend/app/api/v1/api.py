from fastapi import APIRouter
from .endpoints import auth, servers, metrics, alerts, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

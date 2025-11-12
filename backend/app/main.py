import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .core import settings
from .api import api_router
from .db import Base, engine, get_db
from .models import Server
from .services import prometheus_service

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to Vigil - DevOps Monitoring Backend",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint for the application itself.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws/metrics/{server_id}")
async def websocket_metrics(websocket: WebSocket, server_id: int):
    """
    WebSocket endpoint for real-time server metrics.
    Streams metrics every N seconds.
    """
    await websocket.accept()

    # Get database session
    db = next(get_db())

    try:
        # Verify server exists
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            await websocket.send_json({"error": "Server not found"})
            await websocket.close()
            return

        if not server.is_active:
            await websocket.send_json({"error": "Server is not active"})
            await websocket.close()
            return

        # Stream metrics in a loop
        while True:
            try:
                # Fetch metrics from Prometheus
                metrics = await prometheus_service.get_server_metrics(
                    job_name=server.job_name,
                    instance=server.instance
                )

                # Send metrics to client
                await websocket.send_json({
                    "server_id": server.id,
                    "server_name": server.name,
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                    "metrics": metrics
                })

                # Wait before next update
                await asyncio.sleep(settings.WS_METRICS_INTERVAL_SECONDS)

            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({"error": str(e)})
                break

    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    print(f"Shutting down {settings.PROJECT_NAME}")

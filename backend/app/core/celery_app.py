from celery import Celery
from celery.schedules import crontab
from .config import settings

celery_app = Celery(
    "vigil",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "check-alert-rules": {
        "task": "app.services.alert_service.check_alert_rules",
        "schedule": settings.ALERT_CHECK_INTERVAL_SECONDS,
    },
}

# Import tasks to register them
celery_app.autodiscover_tasks(["app.services"])

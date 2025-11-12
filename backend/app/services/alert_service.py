import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..core.celery_app import celery_app
from ..db.session import SessionLocal
from ..models import AlertRule, AlertEvent, Server
from .prometheus_service import prometheus_service
from .telegram_service import telegram_service


def compare_values(value: float, threshold: float, comparison: str) -> bool:
    """
    Compare value against threshold using the given comparison operator.
    """
    if comparison == ">":
        return value > threshold
    elif comparison == "<":
        return value < threshold
    elif comparison == ">=":
        return value >= threshold
    elif comparison == "<=":
        return value <= threshold
    elif comparison == "==":
        return value == threshold
    elif comparison == "!=":
        return value != threshold
    return False


async def process_alert_rule(db: Session, rule: AlertRule):
    """
    Process a single alert rule: query Prometheus and trigger alert if needed.
    """
    # Get server info
    server = db.query(Server).filter(Server.id == rule.server_id).first()
    if not server or not server.is_active:
        return

    # Execute PromQL query
    result = await prometheus_service.query(rule.promql)
    if not result or not result.get("result"):
        return

    # Extract metric value
    try:
        value = float(result["result"][0]["value"][1])
    except (IndexError, ValueError, KeyError):
        return

    # Check if alert should be triggered
    should_alert = compare_values(value, rule.threshold, rule.comparison)

    # Check for recent alerts to respect repeat_interval
    recent_cutoff = datetime.utcnow() - timedelta(seconds=rule.repeat_interval_sec)
    recent_alert = (
        db.query(AlertEvent)
        .filter(
            AlertEvent.alert_rule_id == rule.id,
            AlertEvent.status == "triggered",
            AlertEvent.created_at >= recent_cutoff,
        )
        .first()
    )

    if should_alert and not recent_alert:
        # Create alert event
        alert_event = AlertEvent(
            alert_rule_id=rule.id,
            server_id=server.id,
            metric_name=rule.metric_name,
            value=value,
            status="triggered",
        )
        db.add(alert_event)
        db.commit()

        # Send notification
        if rule.channel == "telegram":
            await telegram_service.send_alert(
                server_name=server.name,
                alert_name=rule.name,
                metric_name=rule.metric_name,
                value=value,
                threshold=rule.threshold,
                comparison=rule.comparison,
                status="triggered",
            )


@celery_app.task(name="app.services.alert_service.check_alert_rules")
def check_alert_rules():
    """
    Celery task to check all active alert rules.
    """
    db = SessionLocal()
    try:
        # Get all active alert rules
        rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()

        # Process each rule
        for rule in rules:
            try:
                asyncio.run(process_alert_rule(db, rule))
            except Exception as e:
                print(f"Error processing alert rule {rule.id}: {e}")

    finally:
        db.close()

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....db import get_db
from ....models import AlertRule, AlertEvent, Server, User
from ....schemas import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertEventResponse,
)
from ....services import get_current_user

router = APIRouter()


# Alert Rules endpoints
@router.get("/rules/", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    skip: int = 0,
    limit: int = 100,
    server_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve list of alert rules.
    """
    query = db.query(AlertRule)
    if server_id:
        query = query.filter(AlertRule.server_id == server_id)
    rules = query.offset(skip).limit(limit).all()
    return rules


@router.post("/rules/", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_in: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new alert rule.
    """
    # Verify server exists
    server = db.query(Server).filter(Server.id == rule_in.server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    # Validate comparison operator
    valid_comparisons = [">", "<", ">=", "<=", "==", "!="]
    if rule_in.comparison not in valid_comparisons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid comparison operator. Must be one of: {', '.join(valid_comparisons)}"
        )

    rule = AlertRule(**rule_in.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get alert rule by ID.
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    return rule


@router.patch("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_in: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an alert rule.
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )

    update_data = rule_in.dict(exclude_unset=True)

    # Validate comparison operator if provided
    if "comparison" in update_data:
        valid_comparisons = [">", "<", ">=", "<=", "==", "!="]
        if update_data["comparison"] not in valid_comparisons:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid comparison operator. Must be one of: {', '.join(valid_comparisons)}"
            )

    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an alert rule.
    """
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )

    db.delete(rule)
    db.commit()
    return None


# Alert Events endpoints
@router.get("/events/", response_model=List[AlertEventResponse])
async def list_alert_events(
    skip: int = 0,
    limit: int = 100,
    server_id: int = None,
    alert_rule_id: int = None,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve list of alert events.
    """
    query = db.query(AlertEvent).order_by(AlertEvent.created_at.desc())

    if server_id:
        query = query.filter(AlertEvent.server_id == server_id)
    if alert_rule_id:
        query = query.filter(AlertEvent.alert_rule_id == alert_rule_id)
    if status_filter:
        query = query.filter(AlertEvent.status == status_filter)

    events = query.offset(skip).limit(limit).all()
    return events


@router.get("/events/{event_id}", response_model=AlertEventResponse)
async def get_alert_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get alert event by ID.
    """
    event = db.query(AlertEvent).filter(AlertEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert event not found"
        )
    return event

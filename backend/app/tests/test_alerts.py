import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from ..models import Server, AlertRule, AlertEvent
from ..services.alert_service import compare_values, process_alert_rule


@pytest.fixture
def test_server(db_session):
    """
    Create a test server.
    """
    server = Server(
        name="Test Server",
        job_name="node",
        instance="localhost:9100",
        is_active=True
    )
    db_session.add(server)
    db_session.commit()
    db_session.refresh(server)
    return server


@pytest.fixture
def test_alert_rule(db_session, test_server):
    """
    Create a test alert rule.
    """
    rule = AlertRule(
        name="High CPU Alert",
        server_id=test_server.id,
        metric_name="cpu_usage",
        promql='avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100',
        threshold=80.0,
        comparison=">",
        repeat_interval_sec=300,
        is_active=True,
        channel="telegram"
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


def test_create_alert_rule(client, auth_headers, test_server):
    """
    Test creating a new alert rule.
    """
    rule_data = {
        "name": "Memory Alert",
        "server_id": test_server.id,
        "metric_name": "memory_usage",
        "promql": "node_memory_usage_percent",
        "threshold": 90.0,
        "comparison": ">",
        "repeat_interval_sec": 300,
        "is_active": True,
        "channel": "telegram"
    }
    response = client.post(
        "/api/v1/alerts/rules/",
        json=rule_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == rule_data["name"]
    assert data["threshold"] == rule_data["threshold"]


def test_create_alert_rule_invalid_comparison(client, auth_headers, test_server):
    """
    Test creating alert rule with invalid comparison operator.
    """
    rule_data = {
        "name": "Invalid Alert",
        "server_id": test_server.id,
        "metric_name": "cpu_usage",
        "promql": "cpu_query",
        "threshold": 80.0,
        "comparison": "invalid",
        "repeat_interval_sec": 300,
        "is_active": True,
        "channel": "telegram"
    }
    response = client.post(
        "/api/v1/alerts/rules/",
        json=rule_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_alert_rule_nonexistent_server(client, auth_headers):
    """
    Test creating alert rule for non-existent server.
    """
    rule_data = {
        "name": "Test Alert",
        "server_id": 9999,
        "metric_name": "cpu_usage",
        "promql": "cpu_query",
        "threshold": 80.0,
        "comparison": ">",
        "repeat_interval_sec": 300,
        "is_active": True,
        "channel": "telegram"
    }
    response = client.post(
        "/api/v1/alerts/rules/",
        json=rule_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_alert_rules(client, auth_headers, test_alert_rule):
    """
    Test listing alert rules.
    """
    response = client.get("/api/v1/alerts/rules/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_alert_rule(client, auth_headers, test_alert_rule):
    """
    Test getting a specific alert rule.
    """
    response = client.get(
        f"/api/v1/alerts/rules/{test_alert_rule.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_alert_rule.id
    assert data["name"] == test_alert_rule.name


def test_update_alert_rule(client, auth_headers, test_alert_rule):
    """
    Test updating an alert rule.
    """
    update_data = {
        "threshold": 90.0,
        "is_active": False
    }
    response = client.patch(
        f"/api/v1/alerts/rules/{test_alert_rule.id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["threshold"] == 90.0
    assert data["is_active"] is False


def test_delete_alert_rule(client, auth_headers, test_alert_rule):
    """
    Test deleting an alert rule.
    """
    response = client.delete(
        f"/api/v1/alerts/rules/{test_alert_rule.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_list_alert_events(client, auth_headers, db_session, test_alert_rule, test_server):
    """
    Test listing alert events.
    """
    # Create a test alert event
    event = AlertEvent(
        alert_rule_id=test_alert_rule.id,
        server_id=test_server.id,
        metric_name="cpu_usage",
        value=85.5,
        status="triggered"
    )
    db_session.add(event)
    db_session.commit()

    response = client.get("/api/v1/alerts/events/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_compare_values():
    """
    Test the compare_values function.
    """
    assert compare_values(85, 80, ">") is True
    assert compare_values(75, 80, ">") is False
    assert compare_values(75, 80, "<") is True
    assert compare_values(85, 80, "<") is False
    assert compare_values(80, 80, ">=") is True
    assert compare_values(85, 80, ">=") is True
    assert compare_values(75, 80, ">=") is False
    assert compare_values(80, 80, "<=") is True
    assert compare_values(75, 80, "<=") is True
    assert compare_values(85, 80, "<=") is False
    assert compare_values(80, 80, "==") is True
    assert compare_values(85, 80, "==") is False
    assert compare_values(85, 80, "!=") is True
    assert compare_values(80, 80, "!=") is False


@pytest.mark.asyncio
@patch("app.services.alert_service.prometheus_service.query")
@patch("app.services.alert_service.telegram_service.send_alert")
async def test_process_alert_rule_triggered(
    mock_telegram,
    mock_prometheus,
    db_session,
    test_alert_rule,
    test_server
):
    """
    Test processing an alert rule that should be triggered.
    """
    # Mock Prometheus returning a high value
    mock_prometheus.return_value = {
        "result": [{"value": [0, "85.5"]}]
    }
    mock_telegram.return_value = True

    await process_alert_rule(db_session, test_alert_rule)

    # Check that an alert event was created
    event = db_session.query(AlertEvent).filter(
        AlertEvent.alert_rule_id == test_alert_rule.id
    ).first()
    assert event is not None
    assert event.status == "triggered"
    assert event.value == 85.5


@pytest.mark.asyncio
@patch("app.services.alert_service.prometheus_service.query")
async def test_process_alert_rule_not_triggered(
    mock_prometheus,
    db_session,
    test_alert_rule,
    test_server
):
    """
    Test processing an alert rule that should not be triggered.
    """
    # Mock Prometheus returning a low value
    mock_prometheus.return_value = {
        "result": [{"value": [0, "50.0"]}]
    }

    await process_alert_rule(db_session, test_alert_rule)

    # Check that no alert event was created
    event = db_session.query(AlertEvent).filter(
        AlertEvent.alert_rule_id == test_alert_rule.id
    ).first()
    assert event is None

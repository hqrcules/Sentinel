import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from ..models import Server


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
def mock_prometheus_metrics():
    """
    Mock Prometheus metrics response.
    """
    return {
        "cpu_usage_percent": 45.5,
        "memory_usage_percent": 60.2,
        "disk_usage_percent": 35.8,
        "network_rx_bytes_per_sec": 1024.5,
        "network_tx_bytes_per_sec": 2048.3,
    }


@patch("app.services.prometheus_service.prometheus_service.get_server_metrics")
def test_get_server_metrics_summary(
    mock_get_metrics,
    client,
    auth_headers,
    test_server,
    mock_prometheus_metrics
):
    """
    Test getting server metrics summary.
    """
    # Mock the Prometheus service response
    mock_get_metrics.return_value = mock_prometheus_metrics

    response = client.get(
        f"/api/v1/metrics/servers/{test_server.id}/summary",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["server_id"] == test_server.id
    assert data["server_name"] == test_server.name
    assert "metrics" in data
    assert data["metrics"]["cpu_usage_percent"] == 45.5


@patch("app.services.prometheus_service.prometheus_service.get_server_metrics")
def test_get_metrics_server_not_found(
    mock_get_metrics,
    client,
    auth_headers
):
    """
    Test getting metrics for non-existent server.
    """
    response = client.get(
        "/api/v1/metrics/servers/9999/summary",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@patch("app.services.prometheus_service.prometheus_service.get_server_metrics")
def test_get_metrics_inactive_server(
    mock_get_metrics,
    client,
    auth_headers,
    db_session
):
    """
    Test getting metrics for inactive server.
    """
    # Create an inactive server
    server = Server(
        name="Inactive Server",
        job_name="node",
        instance="inactive:9100",
        is_active=False
    )
    db_session.add(server)
    db_session.commit()
    db_session.refresh(server)

    response = client.get(
        f"/api/v1/metrics/servers/{server.id}/summary",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("app.services.prometheus_service.prometheus_service.get_server_metrics")
def test_get_metrics_unauthorized(
    mock_get_metrics,
    client,
    test_server
):
    """
    Test getting metrics without authentication.
    """
    response = client.get(f"/api/v1/metrics/servers/{test_server.id}/summary")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@patch("app.services.prometheus_service.prometheus_service.get_server_metrics")
def test_get_metrics_empty_response(
    mock_get_metrics,
    client,
    auth_headers,
    test_server
):
    """
    Test getting metrics when Prometheus returns empty data.
    """
    # Mock empty metrics
    mock_get_metrics.return_value = {}

    response = client.get(
        f"/api/v1/metrics/servers/{test_server.id}/summary",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["metrics"] == {}

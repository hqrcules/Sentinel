import pytest
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


def test_create_server(client, auth_headers):
    """
    Test creating a new server.
    """
    server_data = {
        "name": "Production Server",
        "job_name": "node",
        "instance": "prod-server:9100",
        "is_active": True
    }
    response = client.post(
        "/api/v1/servers/",
        json=server_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == server_data["name"]
    assert data["job_name"] == server_data["job_name"]
    assert data["instance"] == server_data["instance"]
    assert "id" in data


def test_create_server_unauthorized(client):
    """
    Test creating a server without authentication.
    """
    server_data = {
        "name": "Test Server",
        "job_name": "node",
        "instance": "test:9100",
        "is_active": True
    }
    response = client.post("/api/v1/servers/", json=server_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_servers(client, auth_headers, test_server):
    """
    Test listing servers.
    """
    response = client.get("/api/v1/servers/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == test_server.name


def test_get_server(client, auth_headers, test_server):
    """
    Test getting a specific server.
    """
    response = client.get(
        f"/api/v1/servers/{test_server.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_server.id
    assert data["name"] == test_server.name


def test_get_server_not_found(client, auth_headers):
    """
    Test getting a non-existent server.
    """
    response = client.get("/api/v1/servers/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_server(client, auth_headers, test_server):
    """
    Test updating a server.
    """
    update_data = {
        "name": "Updated Server Name",
        "is_active": False
    }
    response = client.patch(
        f"/api/v1/servers/{test_server.id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["is_active"] == update_data["is_active"]


def test_update_server_not_found(client, auth_headers):
    """
    Test updating a non-existent server.
    """
    update_data = {"name": "New Name"}
    response = client.patch(
        "/api/v1/servers/9999",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_server(client, auth_headers, test_server):
    """
    Test deleting a server.
    """
    response = client.delete(
        f"/api/v1/servers/{test_server.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify server is deleted
    response = client.get(
        f"/api/v1/servers/{test_server.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_server_not_found(client, auth_headers):
    """
    Test deleting a non-existent server.
    """
    response = client.delete("/api/v1/servers/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

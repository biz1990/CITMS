import pytest
import requests
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "YOUR_TEST_JWT_TOKEN" # In real tests, get this from a login fixture

@pytest.fixture
def auth_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Trace-Id": str(uuid.uuid4())
    }

def test_health_check():
    """Test system health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_devices(auth_headers):
    """Test listing devices (Asset Management)."""
    response = requests.get(f"{BASE_URL}/devices", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_ticket(auth_headers):
    """Test creating a support ticket (ITSM)."""
    payload = {
        "title": "Test Ticket from Pytest",
        "description": "This is a test ticket for API validation.",
        "priority": "MEDIUM",
        "category": "HARDWARE"
    }
    response = requests.post(f"{BASE_URL}/tickets", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data

def test_get_notifications(auth_headers):
    """Test getting notification history (Notification Engine)."""
    response = requests.get(f"{BASE_URL}/notifications", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_asset_inventory_report_json(auth_headers):
    """Test generating asset inventory report in JSON format."""
    response = requests.get(f"{BASE_URL}/reports/asset-inventory?format=json", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_invalid_login():
    """Test login with invalid credentials (RFC 7807 validation)."""
    payload = {
        "username": "wrong_user",
        "password": "wrong_password"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=payload)
    assert response.status_code == 401
    data = response.json()
    # RFC 7807 checks
    assert "title" in data
    assert "status" in data
    assert data["status"] == 401
    assert "trace_id" in data

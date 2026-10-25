"""Security and input validation tests."""

import pytest
from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_security_headers_present(client):
    """Verify standard defense-in-depth security headers are applied."""
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Content-Security-Policy" in response.headers
    assert "Referrer-Policy" in response.headers


def test_reject_negative_budget(client):
    """Verify API rejects negative budget values with 400 Bad Request."""
    payload = {"budget": -500}
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_reject_invalid_string_budget(client):
    """Verify API rejects non-numeric budget values."""
    payload = {"budget": "invalid_amount"}
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_reject_negative_attendees(client):
    """Verify API rejects negative attendees."""
    payload = {"attendees": -10}
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_reject_excessive_budget(client):
    """Verify API rejects unrealistically huge budget amounts."""
    payload = {"budget": 10**12}
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_reject_invalid_attendee_type(client):
    """Verify non-integer attendee counts are rejected."""
    payload = {"attendees": "not_a_number"}
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 400


def test_generate_endpoint_validation_failure(client):
    """Verify /generate also rejects invalid inputs."""
    payload = {"budget_usd": -100}
    response = client.post("/generate", json=payload)
    assert response.status_code == 400


def test_command_injection_attempt_neutralized(client):
    """Verify malicious input strings are handled safely."""
    payload = {
        "event_type": "; cat /etc/passwd; rm -rf /; calc.exe",
        "budget_usd": 1000,
        "event_date": "2026-11-20 && whoami",
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data

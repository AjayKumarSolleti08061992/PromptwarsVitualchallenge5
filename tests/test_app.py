"""Unit and integration tests for the Flask conference application."""

import pytest
from app import app, EVENTS_DATA


@pytest.fixture
def client():
    """Create a test client for the application."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test that the index route renders successfully."""
    response = client.get("/")
    assert response.status_code == 200
    has_summit = b"Google Cloud Technologies Summit" in response.data
    has_planner = b"Event Planner" in response.data
    assert has_summit or has_planner


def test_schedule_endpoint_returns_json(client):
    """Test that /api/schedule returns valid JSON list of events."""
    response = client.get("/api/schedule")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == len(EVENTS_DATA)
    first = data[0]
    assert "id" in first
    assert "title" in first
    assert "time" in first
    assert "category" in first


def test_schedule_endpoint_cache_headers(client):
    """Test that /api/schedule includes caching headers."""
    response = client.get("/api/schedule")
    assert "Cache-Control" in response.headers
    assert "public" in response.headers["Cache-Control"]


def test_generate_plan_valid_payload(client):
    """Test /api/generate_plan with valid event IDs and budget."""
    payload = {
        "event_ids": ["T1", "T2"],
        "budget": 8000,
        "attendees": 100,
    }
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data
    assert "summary" in data
    assert data["summary"]["total_events"] == 2
    assert "Scaling Applications with Google Kubernetes Engine" in data["plan"]


def test_generate_plan_empty_payload(client):
    """Test /api/generate_plan defaults to all events when no IDs passed."""
    response = client.post("/api/generate_plan", json={})
    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data
    assert "summary" in data
    assert data["summary"]["total_events"] == len(EVENTS_DATA)


def test_generate_plan_unmatched_ids(client):
    """Test /api/generate_plan defaults to all events if IDs unmatched."""
    payload = {"event_ids": ["NON_EXISTENT_ID"]}
    response = client.post("/api/generate_plan", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["summary"]["total_events"] == len(EVENTS_DATA)


def test_generate_plan_custom_time_format(client, monkeypatch):
    """Test /api/generate_plan when event has non-standard time format."""
    mock_events = [
        {
            "id": "C1",
            "title": "Keynote",
            "time": "All Day",
            "type": "talk",
            "category_name": "General",
        }
    ]
    monkeypatch.setattr("app.EVENTS_DATA", mock_events)
    response = client.post("/api/generate_plan", json={"event_ids": ["C1"]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["summary"]["total_events"] == 1


def test_generate_endpoint_legacy(client):
    """Test /generate and /api/generate endpoints."""
    payload = {
        "event_type": "Hackathon",
        "budget_usd": 5000,
        "event_date": "2026-11-20",
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data
    assert "HACKATHON" in data["plan"]

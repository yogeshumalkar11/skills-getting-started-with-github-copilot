"""
Pytest configuration and shared fixtures for test suite.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Arrange: Initialize test client for making requests to the API.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities(monkeypatch):
    """
    Arrange: Set up clean test activities before each test.
    Uses monkeypatch to replace the global activities dictionary
    with a fresh copy to ensure test isolation.
    """
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }
    monkeypatch.setattr("src.app.activities", test_activities)
    return test_activities

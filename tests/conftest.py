"""Pytest configuration and shared fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture
def client():
    """FastAPI TestClient for making HTTP requests."""
    return TestClient(app)


@pytest.fixture
def original_activities():
    """Backup of original activities data."""
    # Import here to get fresh reference
    from app import activities as app_activities
    return deepcopy(app_activities)


@pytest.fixture(autouse=True)
def reset_activities(original_activities):
    """Reset activities data before each test to ensure isolation."""
    from app import activities as app_activities
    app_activities.clear()
    app_activities.update(deepcopy(original_activities))


@pytest.fixture
def sample_student():
    """Sample student email for testing."""
    return "test@mergington.edu"


@pytest.fixture
def available_activity():
    """Name of an activity with available spots."""
    return "Chess Club"  # Has 2 participants, max 12


@pytest.fixture
def full_activity():
    """Name of an activity that's full (for testing capacity limits)."""
    # Find or create a full activity
    for name, details in activities.items():
        if len(details["participants"]) >= details["max_participants"]:
            return name
    # If none are full, return None
    return None
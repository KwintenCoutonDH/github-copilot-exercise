"""Tests for GET /activities endpoint."""

import pytest


class TestGetActivities:
    """Test cases for retrieving activities."""

    def test_get_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Should return a dictionary of activities
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have activities

        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity

    def test_activity_structure(self, client):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        data = response.json()

        for name, details in data.items():
            assert isinstance(name, str)
            assert isinstance(details, dict)

            # Check required fields exist and have correct types
            assert isinstance(details["description"], str)
            assert isinstance(details["schedule"], str)
            assert isinstance(details["max_participants"], int)
            assert isinstance(details["participants"], list)

            # Check max_participants is positive
            assert details["max_participants"] > 0

            # Check participants are strings (emails)
            for participant in details["participants"]:
                assert isinstance(participant, str)
                if participant:  # Only check non-empty
                    assert "@" in participant  # Basic email validation

    def test_participant_count_calculation(self, client):
        """Test that participant counts are accurate."""
        response = client.get("/activities")
        data = response.json()

        for name, details in data.items():
            actual_count = len(details["participants"])
            max_capacity = details["max_participants"]

            # Participant count should not exceed max
            assert actual_count <= max_capacity

            # Calculate available spots
            available = max_capacity - actual_count
            assert available >= 0
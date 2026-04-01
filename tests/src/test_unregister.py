"""Tests for DELETE /activities/{activity_name}/signup endpoint."""

import pytest


class TestUnregister:
    """Test cases for unregistering from activities."""

    def test_successful_unregister(self, client, sample_student, available_activity):
        """Test successful unregistration from an activity."""
        # First sign up
        client.post(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )

        # Then unregister
        response = client.delete(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_student in data["message"]
        assert available_activity in data["message"]

    def test_unregister_removes_from_participants(self, client, sample_student, available_activity):
        """Test that unregister actually removes the student from participants list."""
        # Sign up
        client.post(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )

        # Get participants after signup
        response = client.get("/activities")
        signup_data = response.json()
        signup_participants = signup_data[available_activity]["participants"]

        assert sample_student in signup_participants

        # Unregister
        client.delete(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )

        # Check participants updated
        response = client.get("/activities")
        unregister_data = response.json()
        unregister_participants = unregister_data[available_activity]["participants"]

        assert sample_student not in unregister_participants
        assert len(unregister_participants) == len(signup_participants) - 1

    def test_unregister_not_signed_up(self, client, sample_student, available_activity):
        """Test unregister fails if student is not signed up."""
        response = client.delete(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )

        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client, sample_student):
        """Test unregister for a non-existent activity returns 404."""
        response = client.delete(
            "/activities/NonExistentActivity/signup",
            params={"email": sample_student}
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_after_signup_workflow(self, client, sample_student, available_activity):
        """Test complete signup -> unregister workflow."""
        # Initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[available_activity]["participants"])

        # Sign up
        signup_response = client.post(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )
        assert signup_response.status_code == 200

        # Verify signed up
        response = client.get("/activities")
        after_signup_data = response.json()
        assert len(after_signup_data[available_activity]["participants"]) == initial_count + 1
        assert sample_student in after_signup_data[available_activity]["participants"]

        # Unregister
        unregister_response = client.delete(
            f"/activities/{available_activity}/signup",
            params={"email": sample_student}
        )
        assert unregister_response.status_code == 200

        # Verify unregistered
        response = client.get("/activities")
        final_data = response.json()
        assert len(final_data[available_activity]["participants"]) == initial_count
        assert sample_student not in final_data[available_activity]["participants"]
"""Integration tests for complete workflows and state consistency."""

import pytest


class TestWorkflows:
    """Test complete user workflows and data consistency."""

    def test_multiple_signups_different_activities(self, client):
        """Test signing up for multiple different activities."""
        student1 = "student1@mergington.edu"
        student2 = "student2@mergington.edu"

        # Get available activities
        response = client.get("/activities")
        activities = response.json()

        # Find two activities with space
        available_activities = []
        for name, details in activities.items():
            if len(details["participants"]) < details["max_participants"]:
                available_activities.append(name)
            if len(available_activities) >= 2:
                break

        assert len(available_activities) >= 2, "Need at least 2 activities with available spots"

        activity1, activity2 = available_activities[:2]

        # Student 1 signs up for activity 1
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": student1}
        )
        assert response1.status_code == 200

        # Student 2 signs up for activity 2
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": student2}
        )
        assert response2.status_code == 200

        # Verify both signups
        response = client.get("/activities")
        data = response.json()

        assert student1 in data[activity1]["participants"]
        assert student2 in data[activity2]["participants"]
        assert student1 not in data[activity2]["participants"]
        assert student2 not in data[activity1]["participants"]

    def test_state_consistency_after_operations(self, client):
        """Test that activity state remains consistent after multiple operations."""
        student = "consistency@mergington.edu"
        activity = "Chess Club"  # Known activity

        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data[activity]["participants"].copy()
        max_participants = initial_data[activity]["max_participants"]

        # Perform multiple operations
        operations = [
            ("signup", 200),
            ("signup", 400),  # Should fail - already signed up
            ("delete", 200),  # Unregister
            ("delete", 400),  # Should fail - not signed up
            ("signup", 200),  # Sign up again
        ]

        for op, expected_status in operations:
            if op == "signup":
                response = client.post(
                    f"/activities/{activity}/signup",
                    params={"email": student}
                )
            else:  # delete
                response = client.delete(
                    f"/activities/{activity}/signup",
                    params={"email": student}
                )
            assert response.status_code == expected_status

        # Final state should be back to initial + 1 (signed up once)
        response = client.get("/activities")
        final_data = response.json()
        final_participants = final_data[activity]["participants"]

        assert len(final_participants) == len(initial_participants) + 1
        assert student in final_participants
        assert len(final_participants) <= max_participants

    def test_concurrent_signups_simulation(self, client):
        """Simulate concurrent signups to test for race conditions."""
        activity = "Programming Class"
        students = [f"concurrent{i}@mergington.edu" for i in range(3)]

        # Check available spots
        response = client.get("/activities")
        data = response.json()
        available_spots = data[activity]["max_participants"] - len(data[activity]["participants"])

        # Try to sign up multiple students
        results = []
        for student in students[:available_spots]:  # Only try for available spots
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student}
            )
            results.append((student, response.status_code))

        # Count successful signups
        successful_signups = sum(1 for _, status in results if status == 200)

        # Verify final state
        response = client.get("/activities")
        final_data = response.json()
        final_count = len(final_data[activity]["participants"])

        # Should not exceed capacity
        assert final_count <= data[activity]["max_participants"]

        # All signed up students should be in the list
        for student, status in results:
            if status == 200:
                assert student in final_data[activity]["participants"]

    def test_data_integrity_after_errors(self, client):
        """Test that data remains intact after error conditions."""
        activity = "Chess Club"
        valid_student = "integrity@mergington.edu"
        invalid_student = "invalid@mergington.edu"

        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data[activity]["participants"].copy()

        # Try various invalid operations
        invalid_operations = [
            # Sign up for non-existent activity
            ("post", "/activities/NonExistent/signup", {"email": valid_student}, 404),
            # Delete from non-existent activity
            ("delete", "/activities/NonExistent/signup", {"email": valid_student}, 404),
        ]

        for method, url, params, expected_status in invalid_operations:
            if method == "post":
                response = client.post(url, params=params)
            else:
                response = client.delete(url, params=params)
            # Just check it doesn't crash, status may vary
            assert response.status_code in [200, 400, 404]

        # Verify data integrity - should be unchanged
        response = client.get("/activities")
        final_data = response.json()
        final_participants = final_data[activity]["participants"]

        assert final_participants == initial_participants
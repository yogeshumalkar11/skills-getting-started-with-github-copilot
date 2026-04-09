"""
API tests for the High School Management System using AAA (Arrange-Act-Assert) pattern.
"""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_success(self, client, sample_activities):
        """
        Test that GET /activities returns all activities successfully.
        """
        # Arrange: Client and activities are set up via fixtures

        # Act: Make GET request to activities endpoint
        response = client.get("/activities")

        # Assert: Verify successful response with all activities
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participant_info(self, client, sample_activities):
        """
        Test that activity data includes all participant information.
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
        assert data["Programming Class"]["participants"] == ["emma@mergington.edu"]
        assert data["Gym Class"]["participants"] == []

    def test_get_activities_includes_activity_details(self, client, sample_activities):
        """
        Test that activities include all required details.
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess = data["Chess Club"]
        assert chess["description"] == "Learn strategies and compete in chess tournaments"
        assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess["max_participants"] == 12


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_succeeds(self, client, sample_activities):
        """
        Test that a new student can successfully sign up for an activity.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "alice@mergington.edu"

        # Act: Submit signup request
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Verify successful signup
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in sample_activities[activity_name]["participants"]

    def test_signup_increases_participant_count(self, client, sample_activities):
        """
        Test that signing up increases the participant count for an activity.
        """
        # Arrange
        activity_name = "Gym Class"
        initial_count = len(sample_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email=bob@mergington.edu"
        )

        # Assert
        assert response.status_code == 200
        assert len(sample_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_nonexistent_activity_returns_404(self, client, sample_activities):
        """
        Test that signup fails with 404 when activity doesn't exist.
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client, sample_activities):
        """
        Test that signup fails with 400 when student is already registered.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        # Verify participant list unchanged
        assert sample_activities[activity_name]["participants"].count(email) == 1

    def test_signup_multiple_students_for_same_activity(self, client, sample_activities):
        """
        Test that multiple different students can sign up for the same activity.
        """
        # Arrange
        activity_name = "Gym Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act: First student signs up
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email1}"
        )
        # Second student signs up
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email2}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in sample_activities[activity_name]["participants"]
        assert email2 in sample_activities[activity_name]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_student_succeeds(self, client, sample_activities):
        """
        Test that an existing student can successfully unregister from an activity.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Submit unregister request
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in sample_activities[activity_name]["participants"]

    def test_unregister_decreases_participant_count(self, client, sample_activities):
        """
        Test that unregistering decreases the participant count.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        initial_count = len(sample_activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert len(sample_activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_activity_returns_404(self, client, sample_activities):
        """
        Test that unregister fails with 404 when activity doesn't exist.
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "alice@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up_returns_400(self, client, sample_activities):
        """
        Test that unregister fails with 400 when student is not registered.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "not_registered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_multiple_participants(self, client, sample_activities):
        """
        Test that unregistering one student doesn't affect others.
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"

        # Act: Remove one student
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        assert email_to_remove not in sample_activities[activity_name]["participants"]
        assert email_to_keep in sample_activities[activity_name]["participants"]


class TestIntegrationSignupAndUnregister:
    """Integration tests combining signup and unregister operations."""

    def test_signup_then_unregister_sequence(self, client, sample_activities):
        """
        Test the full flow: signup, verify, then unregister.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "new_student@mergington.edu"

        # Act: Sign up student
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: Signup successful
        assert signup_response.status_code == 200
        assert email in sample_activities[activity_name]["participants"]

        # Act: Unregister the same student
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert: Unregister successful
        assert unregister_response.status_code == 200
        assert email not in sample_activities[activity_name]["participants"]

    def test_signup_unregister_signup_sequence(self, client, sample_activities):
        """
        Test that a student can re-signup after unregistering.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "flexible_student@mergington.edu"

        # Act: First signup
        first_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert first_signup.status_code == 200

        # Unregister
        unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister.status_code == 200

        # Re-signup
        second_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert: All operations successful
        assert second_signup.status_code == 200
        assert email in sample_activities[activity_name]["participants"]

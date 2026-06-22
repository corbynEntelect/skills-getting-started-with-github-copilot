"""Tests for the Mergington High School API using AAA pattern (Arrange-Act-Assert)."""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: No setup needed.
        Act: GET /activities
        Assert: Status 200 and response is a dict with activity data.
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_response_structure(self, client):
        """
        Arrange: No setup needed.
        Act: GET /activities
        Assert: Each activity has expected fields.
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """
        Arrange: Select an activity and a new email not yet signed up.
        Act: POST to signup endpoint with valid email.
        Assert: Status 200 and response confirms signup.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_participant_fails(self, client):
        """
        Arrange: Get an existing participant from an activity.
        Act: Try to POST signup for the same participant.
        Assert: Status 400 with appropriate error message.
        """
        # Arrange
        activity_name = "Chess Club"
        # michael@mergington.edu is already in Chess Club participants
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        """
        Arrange: Use an activity name that doesn't exist.
        Act: POST signup to nonexistent activity.
        Assert: Status 404 with appropriate error message.
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Arrange: Select an activity and a new email.
        Act: Signup, then GET /activities to verify participant was added.
        Assert: New participant appears in the activity's participants list.
        """
        # Arrange
        activity_name = "Gym Class"
        email = "verified@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        get_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_existing_participant_success(self, client):
        """
        Arrange: First signup a participant, then prepare to unregister.
        Act: DELETE signup for that participant.
        Assert: Status 200 and response confirms unregistration.
        """
        # Arrange
        activity_name = "Art Club"
        email = "temp@mergington.edu"
        # First signup
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """
        Arrange: Use an email that is NOT in the activity's participants.
        Act: DELETE signup for nonexistent participant.
        Assert: Status 400 with appropriate error message.
        """
        # Arrange
        activity_name = "Science Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """
        Arrange: Use an activity name that doesn't exist.
        Act: DELETE signup from nonexistent activity.
        Assert: Status 404 with appropriate error message.
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_removes_participant_from_activity(self, client):
        """
        Arrange: Signup a participant, confirm they're in the activity.
        Act: Unregister the participant, then GET /activities.
        Assert: Participant is no longer in the activity's participants list.
        """
        # Arrange
        activity_name = "Drama Society"
        email = "temporary@mergington.edu"
        # First signup
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        # Verify signup worked
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

        # Act
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        get_response = client.get("/activities")

        # Assert
        assert unregister_response.status_code == 200
        activities = get_response.json()
        assert email not in activities[activity_name]["participants"]

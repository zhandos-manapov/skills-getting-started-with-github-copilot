from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


BASE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activity_state():
    # Arrange
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASE_ACTIVITIES))

    yield

    # Teardown
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASE_ACTIVITIES))


@pytest.fixture()
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_list_activities_returns_available_activities(client):
    # Arrange
    # No additional setup is required.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_succeeds(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_existing_participant_returns_bad_request(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }

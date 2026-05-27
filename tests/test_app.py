import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activity_data():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_activities_list():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    response = client.post(
        "/activities/Chess%20Club/signup?email=testuser@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up testuser@mergington.edu for Chess Club"
    assert "testuser@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "duplicate-user@mergington.edu"
    response_first = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )
    assert response_first.status_code == 200

    response_second = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )
    assert response_second.status_code == 400
    assert response_second.json()["detail"] == "Student already signed up"


def test_unregister_participant_removes_user():
    response = client.delete(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/signup?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


@pytest.mark.parametrize(
    "method,path",
    [
        ("POST", "/activities/Unknown%20Club/signup?email=test@mergington.edu"),
        ("DELETE", "/activities/Unknown%20Club/signup?email=test@mergington.edu"),
    ],
)
def test_activity_not_found_returns_404(method, path):
    response = client.request(method, path)

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

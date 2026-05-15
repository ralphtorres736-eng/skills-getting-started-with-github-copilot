import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def build_activity_url(activity_name: str, endpoint: str) -> str:
    encoded_name = quote(activity_name, safe="")
    return f"/activities/{encoded_name}/{endpoint}"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success():
    original_activities = copy.deepcopy(activities)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(build_activity_url(activity_name, "signup"), params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]

    activities.clear()
    activities.update(original_activities)


def test_signup_for_activity_duplicate():
    original_activities = copy.deepcopy(activities)
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(build_activity_url(activity_name, "signup"), params={"email": existing_email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"

    activities.clear()
    activities.update(original_activities)


def test_signup_for_activity_not_found():
    response = client.post(build_activity_url("Nonexistent Club", "signup"), params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    original_activities = copy.deepcopy(activities)
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"

    response = client.delete(build_activity_url(activity_name, "participants"), params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]

    activities.clear()
    activities.update(original_activities)


def test_remove_participant_not_found():
    original_activities = copy.deepcopy(activities)
    activity_name = "Chess Club"
    missing_email = "notregistered@mergington.edu"

    response = client.delete(build_activity_url(activity_name, "participants"), params={"email": missing_email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"

    activities.clear()
    activities.update(original_activities)


def test_remove_participant_activity_not_found():
    response = client.delete(build_activity_url("Nonexistent Club", "participants"), params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

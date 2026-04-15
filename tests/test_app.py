import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Test data
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
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    # Add more if needed for tests
}

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the activities dict before each test to ensure isolation
    from src.app import activities
    activities.clear()
    activities.update(test_activities)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

@pytest.mark.parametrize("activity_name,email,expected_status,expected_message", [
    ("Chess Club", "newstudent@mergington.edu", 200, "Signed up newstudent@mergington.edu for Chess Club"),
    ("Programming Class", "emma@mergington.edu", 400, "Student already signed up for this activity"),
    ("Nonexistent Activity", "test@mergington.edu", 404, "Activity not found"),
])
def test_signup_for_activity(activity_name, email, expected_status, expected_message):
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {"message": expected_message}
        # Verify the participant was added
        from src.app import activities
        if activity_name in activities:
            assert email in activities[activity_name]["participants"]
    else:
        assert response.json()["detail"] == expected_message

@pytest.mark.parametrize("activity_name,email,expected_status,expected_message", [
    ("Chess Club", "michael@mergington.edu", 200, "Unregistered michael@mergington.edu from Chess Club"),
    ("Programming Class", "nonexistent@mergington.edu", 400, "Student is not signed up for this activity"),
    ("Nonexistent Activity", "test@mergington.edu", 404, "Activity not found"),
])
def test_unregister_from_activity(activity_name, email, expected_status, expected_message):
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {"message": expected_message}
        # Verify the participant was removed
        from src.app import activities
        if activity_name in activities:
            assert email not in activities[activity_name]["participants"]
    else:
        assert response.json()["detail"] == expected_message

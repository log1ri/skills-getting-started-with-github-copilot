from src.app import activities
import pytest


def test_get_activities(client):
    """GET /activities returns the activities dictionary and 200 status."""
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    chess = data["Chess Club"]
    assert "participants" in chess and isinstance(chess["participants"], list)


def test_signup_success_and_duplicate(client):
    """POST signup succeeds first time, duplicate returns 400."""
    activity = "Art Club"
    email = "tester@example.com"

    # ensure email not already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    payload = resp.json()
    assert f"Signed up {email} for {activity}" in payload.get("message", "")

    # verify participants list updated
    assert email in activities[activity]["participants"]

    # duplicate signup -> expected 400
    resp_dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp_dup.status_code == 400
    assert resp_dup.json().get("detail") == "Student already signed up"


def test_unregister_success_and_not_found(client):
    """DELETE unregister removes a participant; deleting a non-participant yields 404."""
    activity = "Programming Class"
    email = "temp_student@example.com"

    # If not present, add then remove to test flow
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
    assert f"Unregistered {email} from {activity}" in resp.json().get("message", "")

    # attempt to unregister again => 404 Participant not found
    resp_notfound = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp_notfound.status_code == 404
    assert resp_notfound.json().get("detail") == "Participant not found"


def test_signup_capacity_behavior_current(client):
    """
    Capacity test for POST signup.
    Note: current implementation does not enforce max_participants.
    This test documents current behavior (allows signup even when > max_participants).
    """
    activity = "Debate Team"
    max_p = activities[activity]["max_participants"]

    # fill participants up to max_participants
    i = 0
    while len(activities[activity]["participants"]) < max_p:
        dummy = f"dummy_{i}@example.com"
        if dummy not in activities[activity]["participants"]:
            activities[activity]["participants"].append(dummy)
        i += 1

    assert len(activities[activity]["participants"]) >= max_p

    extra_email = "overflow_tester@example.com"
    resp = client.post(f"/activities/{activity}/signup", params={"email": extra_email})

    # Current behavior: signup succeeds (status 200). Adjust this assertion
    # if you implement capacity checks in app.py (then expect 400).
    assert resp.status_code == 200
    assert extra_email in activities[activity]["participants"]

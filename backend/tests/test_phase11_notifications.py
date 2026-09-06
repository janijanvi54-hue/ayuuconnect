"""Phase 11 tests: in-app notifications lifecycle."""
import datetime as dt

from app.cli import seed_demo_command


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _next_weekday(target):
    today = dt.date.today()
    delta = (target - today.weekday()) % 7 or 7
    if delta <= 3:
        delta += 7
    return today + dt.timedelta(days=delta)   # Wednesday=2, Monday=0


def _login(client, email, password="DemoPass@123"):
    return client.post(
        "/api/auth/login", json={"email": email, "password": password}
    ).get_json()["data"]["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _doctor(client):
    return client.get("/api/doctors?department=ayurveda").get_json()["data"]["doctors"][0]["id"]


def test_unread_count_after_booking(client, app):
    _seed(app)
    patient_token = _login(client, "patient@example.test")
    doctor_token = _login(client, "doctor@example.test")
    did = _doctor(client)

    client.post("/api/me/notifications/read-all", headers=_auth(doctor_token))

    resp = client.get("/api/me/notifications/unread-count", headers=_auth(doctor_token))
    assert resp.get_json()["data"]["unread_count"] == 0

    client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={
            "doctor_id": did,
            "date": _next_weekday(2).isoformat(),
            "start_time": "10:00",
        },
    )
    resp = client.get("/api/me/notifications/unread-count", headers=_auth(doctor_token))
    assert resp.get_json()["data"]["unread_count"] == 1

    notifications = client.get("/api/me/notifications", headers=_auth(doctor_token))
    assert notifications.get_json()["data"]["notifications"][0]["type"].lower() == "appointment"


def test_mark_read_and_read_all(client, app):
    _seed(app)
    patient_token = _login(client, "patient@example.test")
    doctor_token = _login(client, "doctor@example.test")
    did = _doctor(client)
    client.post("/api/me/notifications/read-all", headers=_auth(doctor_token))

    client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={"doctor_id": did, "date": _next_weekday(0).isoformat(), "start_time": "10:00"},
    )
    notification_id = client.get(
        "/api/me/notifications", headers=_auth(doctor_token)
    ).get_json()["data"]["notifications"][0]["id"]

    client.post(
        f"/api/me/notifications/{notification_id}/read", headers=_auth(doctor_token)
    )
    resp = client.get("/api/me/notifications/unread-count", headers=_auth(doctor_token))
    assert resp.get_json()["data"]["unread_count"] == 0

    client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={"doctor_id": did, "date": _next_weekday(0).isoformat(), "start_time": "16:00"},
    )
    resp = client.post("/api/me/notifications/read-all", headers=_auth(doctor_token))
    assert resp.get_json()["data"]["marked"] == 1


def test_cannot_mark_others_notification(client, app):
    _seed(app)
    patient_token = _login(client, "patient@example.test")
    doctor_token = _login(client, "doctor@example.test")
    did = _doctor(client)

    client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={"doctor_id": did, "date": _next_weekday(2).isoformat(), "start_time": "10:00"},
    )
    notification_id = client.get(
        "/api/me/notifications", headers=_auth(doctor_token)
    ).get_json()["data"]["notifications"][0]["id"]

    resp = client.post(
        f"/api/me/notifications/{notification_id}/read", headers=_auth(patient_token)
    )
    assert resp.status_code == 404


def test_notifications_require_auth(client, app):
    _seed(app)
    resp = client.get("/api/me/notifications")
    assert resp.status_code == 401

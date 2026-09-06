"""Phase 6 tests: doctor panel dashboard, availability CRUD, patients, records."""
import datetime
import json

from app.cli import seed_demo_command
from app.extensions import db
from app.models import Doctor, DoctorAvailability, Patient, PatientCase, User


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _doctor_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "doctor@example.test", "password": "DemoPass@123"},
    )
    return resp.get_json()["data"]["access_token"]


def _kavita_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "second-doctor@example.test", "password": "DemoPass@123"},
    )
    return resp.get_json()["data"]["access_token"]


def _patient_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "patient@example.test", "password": "DemoPass@123"},
    )
    return resp.get_json()["data"]["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_requires_doctor_role(client, app):
    _seed(app)
    tok = _patient_token(client)
    response = client.get("/api/doctor/dashboard", headers=_auth(tok))
    assert response.status_code == 403
    assert response.get_json()["error_code"] == "AUTH_FORBIDDEN"


def test_dashboard_stats(client, app):
    _seed(app)
    response = client.get(
        "/api/doctor/dashboard", headers=_auth(_doctor_token(client))
    )
    assert response.status_code == 200
    stats = response.get_json()["data"]["stats"]
    assert stats["total_patients"] == 1
    assert stats["active_cases"] == 1
    assert stats["total_records"] == 1
    assert stats["upcoming_appointments"] == 1
    assert stats["pending_appointments"] == 0
    assert stats["scheduled_followups"] == 1
    assert stats["active_slots"] == 6
    assert stats["rating"] == 4.8


def test_empty_dashboard_for_second_doctor(client, app):
    _seed(app)
    response = client.get(
        "/api/doctor/dashboard", headers=_auth(_kavita_token(client))
    )
    stats = response.get_json()["data"]["stats"]
    assert stats["total_patients"] == 0
    assert stats["active_slots"] == 0


def test_list_own_availability(client, app):
    _seed(app)
    response = client.get(
        "/api/doctor/availability", headers=_auth(_doctor_token(client))
    )
    slots = response.get_json()["data"]["availability"]
    assert len(slots) == 6
    assert all(s["is_active"] for s in slots)


def test_add_availability_slot(client, app):
    _seed(app)
    response = client.post(
        "/api/doctor/availability",
        headers=_auth(_doctor_token(client)),
        json={"weekday": 5, "start_time": "09:00", "end_time": "12:00"},
    )
    assert response.status_code == 201
    slot = response.get_json()["data"]["slot"]
    assert slot["weekday"] == 5
    assert slot["start_time"] == "09:00"


def test_add_duplicate_slot_conflict(client, app):
    _seed(app)
    response = client.post(
        "/api/doctor/availability",
        headers=_auth(_doctor_token(client)),
        json={"weekday": 0, "start_time": "10:00", "end_time": "13:00"},
    )
    assert response.status_code == 409
    assert response.get_json()["error_code"] == "CONFLICT"


def test_add_availability_validation(client, app):
    _seed(app)
    bad = [{"weekday": 7}, {"weekday": 0, "start_time": "14:00", "end_time": "13:00"}]
    for payload in bad:
        response = client.post(
            "/api/doctor/availability",
            headers=_auth(_doctor_token(client)),
            json=payload,
        )
        assert response.status_code == 400


def test_update_availability(client, app):
    _seed(app)
    tok = _doctor_token(client)
    slots = client.get("/api/doctor/availability", headers=_auth(tok)).get_json()["data"]["availability"]
    slot_id = slots[0]["id"]
    response = client.patch(
        f"/api/doctor/availability/{slot_id}",
        headers=_auth(tok),
        json={"start_time": "11:00", "end_time": "13:00"},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["slot"]["start_time"] == "11:00"


def test_update_other_doctors_slot_forbidden(client, app):
    _seed(app)
    share = client.post("/api/auth/login", json={"email": "doctor@example.test", "password": "DemoPass@123"}).get_json()["data"]["access_token"]
    slot_id = client.get("/api/doctor/availability", headers=_auth(share)).get_json()["data"]["availability"][0]["id"]
    response = client.patch(
        f"/api/doctor/availability/{slot_id}",
        headers=_auth(_kavita_token(client)),
        json={"is_active": False},
    )
    assert response.status_code == 404


def test_delete_availability_soft(client, app):
    _seed(app)
    tok = _doctor_token(client)
    slot_id = client.get("/api/doctor/availability", headers=_auth(tok)).get_json()["data"]["availability"][0]["id"]
    response = client.delete(f"/api/doctor/availability/{slot_id}", headers=_auth(tok))
    assert response.status_code == 200
    assert response.get_json()["data"]["slot"]["is_active"] is False


def test_list_doctor_patients(client, app):
    _seed(app)
    response = client.get("/api/doctor/patients", headers=_auth(_doctor_token(client)))
    patients = response.get_json()["data"]["patients"]
    assert len(patients) == 1
    assert patients[0]["patient"]["full_name"] == "Priya Sharma"
    assert patients[0]["case"]["status"] == "ACTIVE"


def test_second_doctor_sees_no_patients(client, app):
    _seed(app)
    response = client.get("/api/doctor/patients", headers=_auth(_kavita_token(client)))
    assert response.get_json()["data"]["patients"] == []


def test_patient_records_case_gated(client, app):
    _seed(app)
    patient = db.session.execute(db.select(Patient).join(User).where(User.email == "patient@example.test")).scalar_one()
    response = client.get(
        f"/api/doctor/patients/{patient.id}/records",
        headers=_auth(_kavita_token(client)),
    )
    assert response.status_code == 404


def test_patient_records_full_history(client, app):
    _seed(app)
    patient = db.session.execute(db.select(Patient).join(User).where(User.email == "patient@example.test")).scalar_one()
    response = client.get(
        f"/api/doctor/patients/{patient.id}/records",
        headers=_auth(_doctor_token(client)),
    )
    assert response.status_code == 200
    history = response.get_json()["data"]["history"]
    assert len(history) == 1
    case = history[0]["case"]
    assert case["records_count"] == 1
    records = history[0]["records"]
    assert records[0]["title"] == "Initial assessment - digestive wellness"
    assert records[0]["prescriptions"][0]["medicine"] == "Ashwagandha Churna"
    assert len(history[0]["followups"]) == 1


def test_appointments_list_and_filter(client, app):
    _seed(app)
    tok = _doctor_token(client)
    response = client.get("/api/doctor/appointments", headers=_auth(tok))
    appointments = response.get_json()["data"]["appointments"]
    assert len(appointments) == 1
    assert appointments[0]["status"] == "CONFIRMED"
    assert appointments[0]["patient_name"] == "Priya Sharma"

    response = client.get("/api/doctor/appointments?status=CONFIRMED", headers=_auth(tok))
    assert len(response.get_json()["data"]["appointments"]) == 1

    response = client.get("/api/doctor/appointments?status=BOGUS", headers=_auth(tok))
    assert response.status_code == 400
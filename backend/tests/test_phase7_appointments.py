"""Phase 7 tests: appointment booking, double-booking guard, status flow."""
import datetime as dt

from app.cli import seed_demo_command
from app.extensions import db
from app.models import Appointment, PatientCase, User


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _login(client, email):
    resp = client.post(
        "/api/auth/login", json={"email": email, "password": "DemoPass@123"}
    )
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["data"]["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _register(client, email):
    resp = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "phone": "+91-98999-00001",
            "password": "TestPass@123",
        },
    )
    assert resp.status_code == 201, resp.get_json()
    login = client.post(
        "/api/auth/login", json={"email": email, "password": "TestPass@123"}
    )
    assert login.status_code == 200, login.get_json()
    return login.get_json()["data"]["access_token"]


def _next_weekday(target):
    today = dt.date.today()
    delta = (target - today.weekday()) % 7 or 7
    if delta <= 3:  # stay clear of the seed appointment (today + 3)
        delta += 7
    return today + dt.timedelta(days=delta)


def _doctor_id(client):
    return client.get("/api/doctors?department=ayurveda").get_json()["data"]["doctors"][0]["id"]


def _wed_date():
    return _next_weekday(2)  # Wednesday


def test_free_slots_endpoint(client, app):
    _seed(app)
    did = _doctor_id(client)
    date = _wed_date().isoformat()
    resp = client.get(f"/api/doctors/{did}/slots?date={date}")
    assert resp.status_code == 200
    slots = resp.get_json()["data"]["slots"]
    assert [s["start_time"] for s in slots] == ["10:00", "16:00"]


def test_free_slots_past_date(client, app):
    _seed(app)
    did = _doctor_id(client)
    yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    resp = client.get(f"/api/doctors/{did}/slots?date={yesterday}")
    assert resp.get_json()["data"]["slots"] == []


def test_book_appointment(client, app):
    _seed(app)
    token = _login(client, "patient@example.test")
    did = _doctor_id(client)
    resp = client.post(
        "/api/patients/appointments",
        headers=_auth(token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    )
    assert resp.status_code == 201
    appointment = resp.get_json()["data"]["appointment"]
    assert appointment["status"] == "PENDING"
    assert appointment["doctor_name"] == "Dr. Rajesh Verma"

    rows = db.session.query(Appointment).filter_by(patient_id=1).count()
    assert rows == 2  # seeded confirmed appointment + this one


def test_duplicate_booking_conflict(client, app):
    _seed(app)
    token = _login(client, "patient@example.test")
    did = _doctor_id(client)
    payload = {"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"}
    first = client.post("/api/patients/appointments", headers=_auth(token), json=payload)
    assert first.status_code == 201
    second = client.post("/api/patients/appointments", headers=_auth(token), json=payload)
    assert second.status_code == 409
    assert second.get_json()["error_code"] == "CONFLICT"


def test_book_outside_availability(client, app):
    _seed(app)
    token = _login(client, "patient@example.test")
    did = _doctor_id(client)
    resp = client.post(
        "/api/patients/appointments",
        headers=_auth(token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "09:30"},
    )
    assert resp.status_code == 400


def test_book_past_date(client, app):
    _seed(app)
    token = _login(client, "patient@example.test")
    did = _doctor_id(client)
    resp = client.post(
        "/api/patients/appointments",
        headers=_auth(token),
        json={"doctor_id": did, "date": "2020-01-01", "start_time": "10:00"},
    )
    assert resp.status_code == 400


def test_patient_appointments_list_and_cancel(client, app):
    _seed(app)
    token = _login(client, "patient@example.test")
    did = _doctor_id(client)
    created = client.post(
        "/api/patients/appointments",
        headers=_auth(token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    ).get_json()["data"]["appointment"]

    resp = client.get("/api/patients/appointments", headers=_auth(token))
    assert resp.get_json()["data"]["count"] == 2

    cancel = client.patch(
        f"/api/patients/appointments/{created['id']}/cancel", headers=_auth(token)
    )
    assert cancel.status_code == 200
    assert cancel.get_json()["data"]["appointment"]["status"] == "CANCELLED"


def test_cancel_confirmed_appointment_allowed(client, app):
    _seed(app)
    patient_token = _login(client, "patient@example.test")
    doctor_token = _login(client, "doctor@example.test")
    did = _doctor_id(client)
    created = client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    ).get_json()["data"]["appointment"]
    client.patch(
        f"/api/doctor/appointments/{created['id']}",
        headers=_auth(doctor_token),
        json={"status": "CONFIRMED"},
    )
    cancel = client.patch(
        f"/api/patients/appointments/{created['id']}/cancel", headers=_auth(patient_token)
    )
    assert cancel.get_json()["data"]["appointment"]["status"] == "CANCELLED"


def test_doctor_status_flow_and_case_creation(client, app):
    _seed(app)
    patient_token = _register(client, "new-patient@example.test")
    doctor_token = _login(client, "doctor@example.test")
    patient_id = client.get("/api/patients/profile", headers=_auth(patient_token)).get_json()["data"]["patient"]["id"]

    did = _doctor_id(client)
    created = client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    ).get_json()["data"]["appointment"]

    confirm = client.patch(
        f"/api/doctor/appointments/{created['id']}",
        headers=_auth(doctor_token),
        json={"status": "CONFIRMED"},
    )
    assert confirm.status_code == 200

    case = db.session.query(PatientCase).filter_by(
        patient_id=patient_id, doctor_id=did
    ).first()
    assert case is not None

    complete = client.patch(
        f"/api/doctor/appointments/{created['id']}",
        headers=_auth(doctor_token),
        json={"status": "COMPLETED"},
    )
    assert complete.status_code == 200


def test_doctor_illegal_transition(client, app):
    _seed(app)
    token = _login(client, "patient@example.test")
    doctor_token = _login(client, "doctor@example.test")
    did = _doctor_id(client)
    created = client.post(
        "/api/patients/appointments",
        headers=_auth(token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    ).get_json()["data"]["appointment"]
    resp = client.patch(
        f"/api/doctor/appointments/{created['id']}",
        headers=_auth(doctor_token),
        json={"status": "COMPLETED"},
    )
    assert resp.status_code == 400


def test_doctor_cannot_touch_other_doctors_appointment(client, app):
    _seed(app)
    patient_token = _login(client, "patient@example.test")
    kavita_token = _login(client, "second-doctor@example.test")
    did = _doctor_id(client)
    created = client.post(
        "/api/patients/appointments",
        headers=_auth(patient_token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    ).get_json()["data"]["appointment"]
    resp = client.patch(
        f"/api/doctor/appointments/{created['id']}",
        headers=_auth(kavita_token),
        json={"status": "CONFIRMED"},
    )
    assert resp.status_code == 404


def test_booking_creates_doctor_notification_and_audit(client, app):
    _seed(app)
    doctor_token = _login(client, "doctor@example.test")
    client.post("/api/me/notifications/read-all", headers=_auth(doctor_token))
    token = _login(client, "patient@example.test")
    did = _doctor_id(client)
    client.post(
        "/api/patients/appointments",
        headers=_auth(token),
        json={"doctor_id": did, "date": _wed_date().isoformat(), "start_time": "10:00"},
    )
    resp = client.get("/api/me/notifications/unread-count", headers=_auth(doctor_token))
    assert resp.get_json()["data"]["unread_count"] == 1

    from app.models import AuditLog
    audit_count = db.session.query(AuditLog).filter_by(action="APPOINTMENT_CREATED").count()
    assert audit_count == 1
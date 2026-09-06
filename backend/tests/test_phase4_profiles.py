"""Phase 4 tests: patient profile and public department/doctor browsing."""

from app.cli import seed_demo_command
from app.extensions import db
from app.models import Department, Gender, Patient


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _register_and_login(client, email="pp@example.test"):
    register = client.post(
        "/api/auth/register",
        json={
            "full_name": "Profile Patient",
            "email": email,
            "phone": "+91-98765-43210",
            "password": "Sup3rSecret!",
        },
    )
    assert register.status_code == 201
    login = client.post(
        "/api/auth/login", json={"email": email, "password": "Sup3rSecret!"}
    )
    return login.get_json()["data"]["access_token"]


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_profile_for_registered_patient(client, app_ctx):
    token = _register_and_login(client)
    response = client.get("/api/patients/profile", headers=_bearer(token))
    assert response.status_code == 200
    body = response.get_json()
    patient = body["data"]["patient"]
    assert patient["email"] == "pp@example.test"
    assert patient["consent_ai"] is True
    assert patient["gender"] is None


def test_update_profile_persists(client, app):
    _seed(app)
    ayurveda = db.session.execute(
        db.select(Department).filter_by(slug="ayurveda")
    ).scalar_one()

    token = _register_and_login(client)
    payload = {
        "full_name": "Priya Sharma Updated",
        "phone": "+91-98111-22222",
        "date_of_birth": "1992-11-03",
        "gender": "FEMALE",
        "blood_group": "B+",
        "emergency_contact": "+91-90000-11111",
        "address": "22 Lotus Lane, Nagpur",
        "department_id": ayurveda.id,
        "consent_records": False,
        "consent_ai": True,
    }
    response = client.put(
        "/api/patients/profile", json=payload, headers=_bearer(token)
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["patient"]["gender"] == "FEMALE"
    assert body["data"]["patient"]["blood_group"] == "B+"
    assert body["data"]["patient"]["date_of_birth"] == "1992-11-03"
    assert body["data"]["patient"]["consent_records"] is False

    # Re-fetch proves persistence.
    again = client.get("/api/patients/profile", headers=_bearer(token))
    stored = again.get_json()["data"]["patient"]
    assert stored["full_name"] == "Priya Sharma Updated"
    assert stored["address"] == "22 Lotus Lane, Nagpur"
    assert stored["department_id"] == ayurveda.id

    patient_row = db.session.execute(
        db.select(Patient)
        .join(Patient.user)
        .where(Patient.user.has(email="pp@example.test"))
    ).scalar_one()
    assert patient_row.gender == Gender.FEMALE


def test_profile_update_validation(client, app):
    _seed(app)
    token = _register_and_login(client)
    bad_payloads = [
        {"gender": "X"},
        {"date_of_birth": "2099-01-01"},
        {"date_of_birth": "not-a-date"},
        {"blood_group": "Z+"},
        {"department_id": 99999},
        {"phone": "abc"},
        {"full_name": ""},
        {"consent_ai": "yes"},
    ]
    for payload in bad_payloads:
        response = client.put(
            "/api/patients/profile", json=payload, headers=_bearer(token)
        )
        assert response.status_code == 400, payload
        assert response.get_json()["error_code"] == "VALIDATION_ERROR"


def test_profile_requires_patient_role(app, client):
    _seed(app)
    login = client.post(
        "/api/auth/login", json={"email": "doctor@example.test", "password": "DemoPass@123"}
    )
    doctor_token = login.get_json()["data"]["access_token"]

    assert client.get("/api/patients/profile").status_code == 401
    denied = client.get("/api/patients/profile", headers=_bearer(doctor_token))
    assert denied.status_code == 403
    assert denied.get_json()["error_code"] == "AUTH_FORBIDDEN"


def test_departments_list_public(client, app):
    _seed(app)
    response = client.get("/api/departments")
    assert response.status_code == 200
    departments = response.get_json()["data"]["departments"]
    assert len(departments) == 4

    slugs = {d["slug"]: d for d in departments}
    assert {"ayurveda", "homeopathy", "unani", "yoga"} == set(slugs)
    # Seeded: one available doctor each in ayurveda and homeopathy.
    assert slugs["ayurveda"]["doctor_count"] == 1
    assert slugs["homeopathy"]["doctor_count"] == 1
    assert slugs["unani"]["doctor_count"] == 0


def test_department_detail(client, app):
    _seed(app)
    ayurveda = db.session.execute(
        db.select(Department).filter_by(slug="ayurveda")
    ).scalar_one()

    response = client.get(f"/api/departments/{ayurveda.id}")
    assert response.status_code == 200
    department = response.get_json()["data"]["department"]
    assert department["name"] == "Ayurveda"

    missing = client.get("/api/departments/99999")
    assert missing.status_code == 404
    assert missing.get_json()["error_code"] == "NOT_FOUND"


def test_department_doctors(client, app):
    _seed(app)
    ayurveda = db.session.execute(
        db.select(Department).filter_by(slug="ayurveda")
    ).scalar_one()

    response = client.get(f"/api/departments/{ayurveda.id}/doctors")
    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["department"]["name"] == "Ayurveda"
    assert len(body["doctors"]) >= 1
    doctor = body["doctors"][0]
    assert doctor["full_name"] == "Dr. Rajesh Verma"
    assert doctor["is_available"] is True
    assert doctor["rating"] == 4.8
    assert "license_no" not in doctor

    missing = client.get("/api/departments/99999/doctors")
    assert missing.status_code == 404
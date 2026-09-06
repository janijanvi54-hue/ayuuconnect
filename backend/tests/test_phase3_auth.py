"""Phase 3 tests: registration, login, JWT guard, and role-based access."""

import jwt as pyjwt

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import AuditLog, Patient, User
from app.utils.decorators import roles_required
from app.utils.response import api_success


def _register(client, email="patient@example.test"):
    return client.post(
        "/api/auth/register",
        json={
            "full_name": "Priya Sharma",
            "email": email,
            "phone": "+91-98765-43210",
            "password": "Sup3rSecret!",
        },
    )


def _register_and_login(client, email="patient@example.test"):
    _register(client, email)
    return client.post(
        "/api/auth/login", json={"email": email, "password": "Sup3rSecret!"}
    )


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_patient_creates_account(client, app_ctx):
    response = _register(client)
    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["user"]["role"] == "PATIENT"
    assert body["data"]["user"]["email"] == "patient@example.test"

    user = db.session.execute(
        db.select(User).filter_by(email="patient@example.test")
    ).scalar_one()
    assert db.session.get(Patient, user.patient.id).consent_ai is True
    assert user.check_password("Sup3rSecret!")


def test_register_rejects_duplicate_email(client):
    assert _register(client).status_code == 201
    response = _register(client)
    assert response.status_code == 409
    body = response.get_json()
    assert body["error_code"] == "CONFLICT"


def test_register_validation_errors(client):
    cases = [
        {},  # completely empty
        {"full_name": "", "email": "bad", "phone": "123", "password": "short"},
        {"full_name": "X", "email": "not-an-email", "phone": "+91-98765-43210", "password": "Sup3rSecret!"},
        {"full_name": "X", "email": "ok@example.test", "phone": "12", "password": "Sup3rSecret!"},
    ]
    for payload in cases:
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 400, payload
        assert response.get_json()["error_code"] == "VALIDATION_ERROR"


def test_login_success_issues_token(client):
    response = _register_and_login(client)
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["user"]["email"] == "patient@example.test"
    assert body["data"]["user"]["role"] == "PATIENT"
    assert body["data"]["user"]["profile"]["blood_group"] is None


def test_login_wrong_password_and_unknown_user(client):
    _register(client)
    for payload in (
        {"email": "patient@example.test", "password": "WrongPass123!"},
        {"email": "nobody@example.test", "password": "Sup3rSecret!"},
    ):
        response = client.post("/api/auth/login", json=payload)
        assert response.status_code == 401
        assert response.get_json()["error_code"] == "AUTH_REQUIRED"


def test_me_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.get_json()["error_code"] == "AUTH_REQUIRED"


def test_me_returns_profile(client):
    login = _register_and_login(client)
    token = login.get_json()["data"]["access_token"]

    response = client.get("/api/auth/me", headers=_bearer(token))
    assert response.status_code == 200
    body = response.get_json()
    assert body["data"]["user"]["email"] == "patient@example.test"
    assert body["data"]["user"]["role"] == "PATIENT"


def test_logout_logs_event(client):
    login = _register_and_login(client)
    token = login.get_json()["data"]["access_token"]

    response = client.post("/api/auth/logout", headers=_bearer(token))
    assert response.status_code == 200
    actions = {log.action for log in db.session.query(AuditLog).all()}
    assert {"LOGIN", "LOGOUT"} <= actions


def test_roles_required_enforces_role(app, client):
    # Register the guarded route before the app handles its first request.
    @app.get("/api/_admin-only")
    @roles_required("ADMIN")
    def admin_only():
        return api_success("admin ok")

    login = _register_and_login(client)
    patient_token = login.get_json()["data"]["access_token"]

    denied = client.get("/api/_admin-only", headers=_bearer(patient_token))
    assert denied.status_code == 403
    assert denied.get_json()["error_code"] == "AUTH_FORBIDDEN"


def test_invalid_token_rejected(client, app):
    with app.app_context():
        user = db.session.execute(
            db.select(User).filter_by(email="patient@example.test")
        ).scalar_one_or_none()

    # A structurally valid JWT signed with a different secret, plus garbage.
    if user is None:
        bad_payload = pyjwt.encode(
            {"sub": 999999, "exp": 9999999999}, "wrong-secret-0123456789abcdef0123456789abcdef", algorithm="HS256"
        )
    else:
        bad_payload = pyjwt.encode(
            {"sub": user.id, "exp": 9999999999}, "wrong-secret-0123456789abcdef0123456789abcdef", algorithm="HS256"
        )

    response = client.get("/api/auth/me", headers=_bearer(bad_payload))
    assert response.status_code == 401
    assert response.get_json()["error_code"] == "AUTH_REQUIRED"


def test_doctor_login_returns_doctor_profile(client, app_ctx):
    from app.models import Department, Doctor, UserRole

    dept = db.session.execute(
        db.select(Department).filter_by(slug="ayurveda")
    ).scalar_one_or_none()
    if dept is None:
        dept = Department(name="Ayurveda", slug="ayurveda")
        db.session.add(dept)
    user = User(email="doc@example.test", full_name="Dr. R", role=UserRole.DOCTOR)
    user.set_password("Sup3rSecret!")
    db.session.add(user)
    db.session.add(Doctor(user=user, department=dept, license_no="LIC-1"))
    db.session.commit()

    response = client.post(
        "/api/auth/login", json={"email": "doc@example.test", "password": "Sup3rSecret!"}
    )
    assert response.status_code == 200
    profile = response.get_json()["data"]["user"]["profile"]
    assert profile["specialization"] is None
    assert profile["department_id"] == dept.id


def test_seeded_admin_can_login(client, app):
    from app.cli import seed_demo_command

    app.test_cli_runner().invoke(seed_demo_command)
    response = client.post(
        "/api/auth/login", json={"email": "admin@example.test", "password": "DemoPass@123"}
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["user"]["role"] == "ADMIN"
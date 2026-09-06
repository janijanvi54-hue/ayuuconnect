"""Phase 10 tests: admin dashboard, users, doctors, departments, audit."""
from app.cli import seed_demo_command


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _admin_token(client):
    resp = client.post(
        "/api/auth/login", json={"email": "admin@example.test", "password": "DemoPass@123"}
    )
    return resp.get_json()["data"]["access_token"]


def _patient_token(client):
    resp = client.post(
        "/api/auth/login", json={"email": "patient@example.test", "password": "DemoPass@123"}
    )
    return resp.get_json()["data"]["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_admin_guard(client, app):
    _seed(app)
    resp = client.get("/api/admin/dashboard", headers=_auth(_patient_token(client)))
    assert resp.status_code == 403


def test_dashboard_stats(client, app):
    _seed(app)
    resp = client.get("/api/admin/dashboard", headers=_auth(_admin_token(client)))
    assert resp.status_code == 200
    stats = resp.get_json()["data"]["stats"]
    assert stats["patients"] == 1
    assert stats["doctors"] == 2
    assert stats["total_users"] == 4
    assert stats["active_departments"] == 4


def test_list_and_filter_users(client, app):
    _seed(app)
    tok = _admin_token(client)
    all_users = client.get("/api/admin/users", headers=_auth(tok)).get_json()["data"]["users"]
    assert len(all_users) == 4

    doctors = client.get(
        "/api/admin/users?role=DOCTOR", headers=_auth(tok)
    ).get_json()["data"]["users"]
    assert len(doctors) == 2

    q = client.get(
        "/api/admin/users?q=priya", headers=_auth(tok)
    ).get_json()["data"]["users"]
    assert len(q) == 1

    bad = client.get("/api/admin/users?role=GOD", headers=_auth(tok))
    assert bad.status_code == 400


def test_cannot_deactivate_self(client, app):
    _seed(app)
    resp = client.patch(
        "/api/admin/users/4", headers=_auth(_admin_token(client)), json={"is_active": False}
    )
    assert resp.status_code == 400


def test_deactivate_patient(client, app):
    _seed(app)
    tok = _admin_token(client)
    resp = client.patch(
        "/api/admin/users/1", headers=_auth(tok), json={"is_active": False}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["user"]["is_active"] is False

    login = client.post(
        "/api/auth/login", json={"email": "patient@example.test", "password": "DemoPass@123"}
    )
    assert login.status_code == 401


def test_create_doctor(client, app):
    _seed(app)
    tok = _admin_token(client)
    resp = client.post(
        "/api/admin/doctors",
        headers=_auth(tok),
        json={
            "email": "dr.new@example.test",
            "full_name": "Dr. New Doctor",
            "phone": "+91-90000-00099",
            "password": "DoctorPass@123",
            "department_id": 1,
            "license_no": "AYUSH-NW-0001",
            "specialization": "General Ayurveda",
            "experience_years": 5,
        },
    )
    assert resp.status_code == 201
    assert resp.get_json()["data"]["user"]["role"] == "DOCTOR"

    duplicate = client.post(
        "/api/admin/doctors",
        headers=_auth(tok),
        json={
            "email": "dr.new@example.test",
            "full_name": "Dr. New Doctor",
            "phone": "+91-90000-00099",
            "password": "DoctorPass@123",
            "department_id": 1,
        },
    )
    assert duplicate.status_code == 409


def test_create_doctor_bad_department(client, app):
    _seed(app)
    resp = client.post(
        "/api/admin/doctors",
        headers=_auth(_admin_token(client)),
        json={
            "email": "dr.bad@example.test",
            "full_name": "Dr. Bad",
            "phone": "+91-90000-00098",
            "password": "DoctorPass@123",
            "department_id": 999,
        },
    )
    assert resp.status_code == 400


def test_create_and_patch_department(client, app):
    _seed(app)
    tok = _admin_token(client)
    resp = client.post(
        "/api/admin/departments",
        headers=_auth(tok),
        json={"name": "Siddha Medicine", "slug": "siddha"},
    )
    assert resp.status_code == 201
    dept_id = resp.get_json()["data"]["department"]["id"]

    duplicated = client.post(
        "/api/admin/departments",
        headers=_auth(tok),
        json={"name": "Siddha Again", "slug": "siddha"},
    )
    assert duplicated.status_code == 409

    patched = client.patch(
        f"/api/admin/departments/{dept_id}",
        headers=_auth(tok),
        json={"is_active": False},
    )
    assert patched.status_code == 200
    assert patched.get_json()["data"]["department"]["is_active"] is False


def test_audit_logs_endpoint(client, app):
    _seed(app)
    tok = _admin_token(client)
    client.get("/api/admin/dashboard", headers=_auth(tok))
    resp = client.get("/api/admin/audit-logs", headers=_auth(tok))
    logs = resp.get_json()["data"]["logs"]
    assert len(logs) >= 4  # login/logout/dashboard/login of seed run + our actions


def test_admin_lists_doctors(client, app):
    _seed(app)
    resp = client.get("/api/admin/doctors", headers=_auth(_admin_token(client)))
    assert len(resp.get_json()["data"]["doctors"]) == 2


def test_admin_patch_doctor(client, app):
    _seed(app)
    tok = _admin_token(client)
    resp = client.patch(
        "/api/admin/doctors/1", headers=_auth(tok), json={"is_available": False}
    )
    assert resp.status_code == 200
    assert resp.get_json()["data"]["doctor"]["is_available"] is False
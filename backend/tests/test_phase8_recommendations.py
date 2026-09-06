"""Phase 8 tests: Check My Health Concern recommendations."""
from app.cli import seed_demo_command


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _login(client, email="patient@example.test"):
    resp = client.post(
        "/api/auth/login", json={"email": email, "password": "DemoPass@123"}
    )
    return resp.get_json()["data"]["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _register(client, email):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "phone": "+91-98999-00002",
            "password": "TestPass@123",
        },
    )
    resp = client.post(
        "/api/auth/login", json={"email": email, "password": "TestPass@123"}
    )
    return resp.get_json()["data"]["access_token"]


def test_create_recommendation(client, app):
    _seed(app)
    token = _login(client)
    resp = client.post(
        "/api/patients/recommendations",
        headers=_auth(token),
        json={"concern": "I feel bloated after meals and have low energy."},
    )
    assert resp.status_code == 201
    rec = resp.get_json()["data"]["recommendation"]
    assert rec["department"]["slug"] == "ayurveda"
    assert rec["category"] == "digestive_wellness"
    assert rec["confidence"] >= 0.8


def test_recommendation_matches_homeopathy(client, app):
    _seed(app)
    token = _login(client)
    resp = client.post(
        "/api/patients/recommendations",
        headers=_auth(token),
        json={"concern": "I have had eczema on my hands for months now."},
    )
    rec = resp.get_json()["data"]["recommendation"]
    assert rec["department"]["slug"] == "homeopathy"


def test_list_recommendations(client, app):
    _seed(app)
    token = _login(client)
    client.post(
        "/api/patients/recommendations",
        headers=_auth(token),
        json={"concern": "sirahkhadi and migraine headaches at night"},
    )
    resp = client.get("/api/patients/recommendations", headers=_auth(token))
    assert resp.get_json()["data"]["recommendations"][0]["category"] == "stress_and_sleep"


def test_short_concern_rejected(client, app):
    _seed(app)
    token = _login(client)
    resp = client.post(
        "/api/patients/recommendations",
        headers=_auth(token),
        json={"concern": "short"},
    )
    assert resp.status_code == 400


def test_consent_gated(client, app):
    _seed(app)
    token = _register(client, "consent@example.test")
    client.put(
        "/api/patients/profile",
        headers=_auth(token),
        json={"consent_ai": False},
    )
    resp = client.post(
        "/api/patients/recommendations",
        headers=_auth(token),
        json={"concern": "I have frequent headaches and poor sleep."},
    )
    assert resp.status_code == 409


def test_doctor_cannot_recommend(client, app):
    _seed(app)
    token = _login(client, "doctor@example.test")
    resp = client.post(
        "/api/patients/recommendations",
        headers=_auth(token),
        json={"concern": "I have stomach pain."},
    )
    assert resp.status_code == 403
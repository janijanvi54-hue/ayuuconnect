"""Phase 9 tests: conversational assistant (chat sessions)."""
import uuid

from app.cli import seed_demo_command


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def _login(client, email=None, password="TestPass@123"):
    """Register + login a brand-new patient (isolates per-test state)."""
    if email is None:
        email = f"chat-{uuid.uuid4().hex[:10]}@example.test"
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Chat Tester",
            "email": email,
            "phone": "+91-98999-00009",
            "password": password,
        },
    )
    resp = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    return resp.get_json()["data"]["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _session(client, token):
    resp = client.post(
        "/api/patients/chat/sessions",
        headers=_auth(token),
        json={"title": "Digestive concerns"},
    )
    assert resp.status_code == 201
    return resp.get_json()["data"]["session"]["id"]


def test_create_and_list_sessions(client, app):
    _seed(app)
    token = _login(client)
    _session(client, token)
    resp = client.get("/api/patients/chat/sessions", headers=_auth(token))
    sessions = resp.get_json()["data"]["sessions"]
    assert len(sessions) == 1
    assert "Digestive" in sessions[0]["title"]


def test_send_message_returns_bot_reply(client, app):
    _seed(app)
    token = _login(client)
    session_id = _session(client, token)
    resp = client.post(
        f"/api/patients/chat/sessions/{session_id}/messages",
        headers=_auth(token),
        json={"content": "I have digestion issues lately"},
    )
    assert resp.status_code == 200
    bot = resp.get_json()["data"]["bot_message"]
    assert bot["sender"] == "BOT"
    assert bot["provider"] == "demo"
    assert "Ayurvedic" in bot["content"]


def test_session_persists_messages(client, app):
    _seed(app)
    token = _login(client)
    session_id = _session(client, token)
    client.post(
        f"/api/patients/chat/sessions/{session_id}/messages",
        headers=_auth(token),
        json={"content": "How do I book?"},
    )
    resp = client.get(f"/api/patients/chat/sessions/{session_id}", headers=_auth(token))
    messages = resp.get_json()["data"]["session"]["messages"]
    assert len(messages) == 2
    assert messages[0]["sender"] == "USER"
    assert messages[1]["sender"] == "BOT"


def test_session_title_defaults_to_first_message(client, app):
    _seed(app)
    token = _login(client)
    resp = client.post("/api/patients/chat/sessions", headers=_auth(token))
    session_id = resp.get_json()["data"]["session"]["id"]
    client.post(
        f"/api/patients/chat/sessions/{session_id}/messages",
        headers=_auth(token),
        json={"content": "My sleep has been terrible"},
    )
    resp = client.get(f"/api/patients/chat/sessions/{session_id}", headers=_auth(token))
    assert "sleep" in resp.get_json()["data"]["session"]["title"].lower()


def test_empty_message_rejected(client, app):
    _seed(app)
    token = _login(client)
    session_id = _session(client, token)
    resp = client.post(
        f"/api/patients/chat/sessions/{session_id}/messages",
        headers=_auth(token),
        json={"content": "   "},
    )
    assert resp.status_code == 400


def test_cannot_access_others_session(client, app):
    _seed(app)
    token = _login(client)
    session_id = _session(client, token)
    other_token = _login(client, email="other@example.test")
    resp = client.get(f"/api/patients/chat/sessions/{session_id}", headers=_auth(other_token))
    assert resp.status_code == 404
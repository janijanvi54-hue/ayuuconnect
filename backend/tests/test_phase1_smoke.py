"""Phase 1 smoke tests: application wiring, envelopes, error handling."""

import pytest


@pytest.mark.parametrize("path", ["/api/health"])
def test_health_endpoint(client, path):
    response = client.get(path)
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "AYUConnect API is running"
    assert body["data"]["database"] == "connected"
    assert body["data"]["service"] == "ayuconnect-api"


def test_method_not_allowed_uses_envelope(client):
    response = client.post("/api/health")
    assert response.status_code == 405
    body = response.get_json()
    assert body["success"] is False
    assert body["error_code"] == "METHOD_NOT_ALLOWED"


def test_unknown_route_uses_envelope(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error_code"] == "NOT_FOUND"


def test_500_does_not_leak_stack_trace(app, client):
    @app.route("/api/_boom")
    def boom():
        raise RuntimeError("secret internal detail")

    response = client.get("/api/_boom")
    assert response.status_code == 500
    body = response.get_json()
    assert body["success"] is False
    assert body["error_code"] == "SERVER_ERROR"
    assert "secret internal detail" not in response.get_data(as_text=True)


def test_config_environments(monkeypatch):
    from app.config import get_config

    assert get_config("development").DEBUG is True
    assert get_config("testing").TESTING is True

    # Production requires explicit secrets and a MySQL URL.
    monkeypatch.setenv("SECRET_KEY", "prod-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "prod-jwt-secret")
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://u:p@db/ayuconnect")
    assert get_config("production").DEBUG is False

    # SQLite is rejected in production.
    monkeypatch.setenv("DATABASE_URL", "sqlite:///x.db")
    with pytest.raises(RuntimeError):
        get_config("production")

    with pytest.raises(ValueError):
        get_config("nope")
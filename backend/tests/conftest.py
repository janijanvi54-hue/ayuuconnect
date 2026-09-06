"""Pytest fixtures shared across the test suite."""

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    """Create an application for the ``testing`` environment.

    Uses an isolated in-memory SQLite database and a fixed JWT secret so
    tests are deterministic and independent of any local configuration.
    """
    application = create_app("testing")
    application.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        JWT_SECRET_KEY="test-jwt-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """HTTP test client bound to the testing application."""
    return app.test_client()


@pytest.fixture()
def app_ctx(app):
    """Provide an active application context for direct service calls."""
    with app.app_context():
        yield app
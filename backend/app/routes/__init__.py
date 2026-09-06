"""API blueprints. New modules register their blueprints here."""

from .health import health_bp


def register_blueprints(app):
    """Register every blueprint with the Flask app."""
    app.register_blueprint(health_bp)
"""API blueprints. New modules register their blueprints here."""

from .admin import admin_bp
from .appointments import appointments_bp
from .auth import auth_bp
from .chat import chat_bp
from .departments import departments_bp
from .doctors import doctors_bp
from .doctors_panel import doctors_panel_bp
from .health import health_bp
from .notifications import notifications_bp
from .patients import patients_bp
from .recommendations import recommendations_bp


def register_blueprints(app):
    """Register every blueprint with the Flask app."""
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(doctors_panel_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
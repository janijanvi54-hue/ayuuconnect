"""JWT wiring: user identity resolution and envelope-shaped token errors."""

from flask.json import jsonify

from .extensions import db
from .models import User


def _jwt_error(message, code="AUTH_REQUIRED", status=401):
    return jsonify({"success": False, "message": message, "error_code": code}), status


def configure_jwt(jwt):
    """Register identity loaders and token-error handlers on ``jwt``."""

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user.id)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_data):
        return _jwt_error("Your access token has expired. Please log in again.")

    @jwt.invalid_token_loader
    def invalid_token_callback(_reason):
        return _jwt_error("Invalid access token. Please log in again.")

    @jwt.unauthorized_loader
    def missing_token_callback(_reason):
        return _jwt_error("Access token is missing. Please log in.")

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_data):
        return _jwt_error("Your access token has been revoked. Please log in again.")
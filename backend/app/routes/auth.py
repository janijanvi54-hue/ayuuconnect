"""Authentication blueprint: register, login, logout, me."""

from flask import Blueprint, request

from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import AuditLog
from ..services.auth_service import (
    authenticate,
    register_patient,
    user_payload,
)
from ..utils.decorators import current_user, roles_required
from ..utils.response import ApiError, api_success

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    """Patient self-registration. Creates the user and profile."""
    user = register_patient(request.get_json(silent=True) or {})
    return api_success(
        "Account created. You can now log in.",
        {"user": user_payload(user)},
        status=201,
    )


@auth_bp.post("/login")
def login():
    """Authenticate email+password and issue a JWT access token."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    user = authenticate(email, data.get("password"))
    if user is None:
        raise ApiError("Invalid email or password.", "AUTH_REQUIRED", 401)
    if not user.is_active:
        raise ApiError(
            "This account is deactivated. Contact support.", "AUTH_REQUIRED", 401
        )

    token = create_access_token(identity=user)

    db.session.add(
        AuditLog(
            user=user,
            action="LOGIN",
            resource="auth",
            ip_address=request.headers.get("X-Forwarded-For") or request.remote_addr,
            details={"method": "password"},
        )
    )
    db.session.commit()

    return api_success(
        "Login successful.",
        {
            "access_token": token,
            "token_type": "bearer",
            "user": user_payload(user),
        },
    )


@auth_bp.post("/logout")
@roles_required("PATIENT", "DOCTOR", "ADMIN")
def logout():
    """Stateless logout: the client discards its token."""
    user = current_user()
    db.session.add(
        AuditLog(
            user=user,
            action="LOGOUT",
            resource="auth",
            ip_address=request.headers.get("X-Forwarded-For") or request.remote_addr,
        )
    )
    db.session.commit()
    return api_success("Logged out.")


@auth_bp.get("/me")
@roles_required("PATIENT", "DOCTOR", "ADMIN")
def me():
    """Return the authenticated user's public profile."""
    return api_success("Current user", {"user": user_payload(current_user())})
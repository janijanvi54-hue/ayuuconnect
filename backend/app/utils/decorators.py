"""Authentication/authorization decorators and current-user helpers."""

from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import User
from .response import ApiError


def current_user():
    """Load the authenticated user from the request, or ``None``."""
    identity = get_jwt_identity()
    if identity is None:
        return None
    try:
        return db.session.get(User, int(identity))
    except (TypeError, ValueError):
        return None


def roles_required(*roles):
    """Require a valid JWT whose user holds one of ``roles``.

    Usage: ``@roles_required("PATIENT", "ADMIN")``
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None or not user.is_active:
                raise ApiError(
                    "Authentication required.", "AUTH_REQUIRED", 401
                )
            if user.role.value not in roles:
                raise ApiError(
                    "You do not have permission to perform this action.",
                    "AUTH_FORBIDDEN",
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
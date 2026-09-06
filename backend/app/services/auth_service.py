"""Authentication business logic: registration, login, and serialization."""

import re

from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Patient, User, UserRole
from ..services.serializers import patient_payload
from ..utils.response import ApiError

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^[+\d][\d\s\-]{7,14}$")
MIN_PASSWORD_LENGTH = 8


def _normalize_email(email):
    return (email or "").strip().lower()


def get_user_by_email(email):
    """Return the user for ``email`` (case-insensitive) or ``None``."""
    return db.session.execute(
        db.select(User).filter_by(email=_normalize_email(email))
    ).scalar_one_or_none()


def validate_register(data):
    """Validate patient registration input; raise ``ApiError`` on failure."""
    full_name = (data.get("full_name") or "").strip()
    email = _normalize_email(data.get("email"))
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not full_name:
        raise ApiError("Full name is required.", "VALIDATION_ERROR", 400)
    if not email or not EMAIL_RE.match(email):
        raise ApiError("A valid email address is required.", "VALIDATION_ERROR", 400)
    if not phone or not PHONE_RE.match(phone):
        raise ApiError("A valid phone number is required.", "VALIDATION_ERROR", 400)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ApiError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters.",
            "VALIDATION_ERROR",
            400,
        )
    return {"full_name": full_name, "email": email, "phone": phone, "password": password}


def register_patient(data):
    """Create a new PATIENT account with its 1:1 patient profile.

    Returns the created :class:`User`. Addresses of duplicate email address.
    """
    cleaned = validate_register(data)

    if get_user_by_email(cleaned["email"]) is not None:
        raise ApiError(
            "An account with this email already exists.", "CONFLICT", 409
        )

    user = User(
        email=cleaned["email"],
        full_name=cleaned["full_name"],
        role=UserRole.PATIENT,
        phone=cleaned["phone"],
        is_active=True,
    )
    user.set_password(cleaned["password"])
    db.session.add(user)
    db.session.add(Patient(user=user, consent_records=True, consent_ai=True))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError(
            "An account with this email already exists.", "CONFLICT", 409
        )
    return user


def authenticate(email, password):
    """Return the :class:`User` for valid credentials, otherwise ``None``."""
    user = get_user_by_email(email)
    if user is None or not user.check_password(password or ""):
        return None
    return user


def user_payload(user):
    """Public representation of a user used by auth and profile endpoints."""
    profile = None
    if user.role == UserRole.PATIENT and user.patient is not None:
        profile = patient_payload(user.patient)
    elif user.role == UserRole.DOCTOR and user.doctor is not None:
        doctor = user.doctor
        profile = {
            "id": doctor.id,
            "department_id": doctor.department_id,
            "specialization": doctor.specialization,
            "is_available": doctor.is_available,
        }
    elif user.role == UserRole.ADMIN and user.admin is not None:
        profile = {"id": user.admin.id}

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "profile": profile,
    }
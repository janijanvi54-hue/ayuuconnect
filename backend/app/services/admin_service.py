"""Admin operations: dashboard, users, doctors, departments, audit."""

import datetime as dt

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import (
    Appointment,
    AuditLog,
    Department,
    Doctor,
    Patient,
    Recommendation,
    User,
    UserRole,
)
from ..services import notification_service
from ..utils.response import ApiError

VALID_DOCTOR_FIELDS = {"specialization", "bio", "experience_years",
                       "license_no", "department_id", "is_available"}


def dashboard_stats():
    today = dt.date.today().isoformat()
    return {
        "patients": db.session.scalar(db.select(func.count(Patient.id))) or 0,
        "doctors": db.session.scalar(db.select(func.count(Doctor.id))) or 0,
        "total_users": db.session.scalar(db.select(func.count(User.id))) or 0,
        "appointments_today": db.session.scalar(
            db.select(func.count(Appointment.id)).where(Appointment.date == today)
        ) or 0,
        "upcoming_appointments": db.session.scalar(
            db.select(func.count(Appointment.id)).where(Appointment.date >= today)
        ) or 0,
        "recommendations": db.session.scalar(
            db.select(func.count(Recommendation.id))
        ) or 0,
        "active_departments": db.session.scalar(
            db.select(func.count(Department.id)).where(Department.is_active.is_(True))
        ) or 0,
    }


def list_users(role=None, query=None, include_inactive=True):
    stmt = db.select(User).order_by(User.created_at.desc())
    if role:
        try:
            parsed = UserRole(str(role).upper())
        except ValueError:
            raise ApiError(
                f"role must be one of {sorted(r.value for r in UserRole)}.",
                "VALIDATION_ERROR",
                400,
            )
        stmt = stmt.where(User.role == parsed)
    if query:
        pattern = f"%{query.strip()}%"
        stmt = stmt.where(
            db.or_(
                User.email.ilike(pattern),
                User.full_name.ilike(pattern),
                User.phone.ilike(pattern),
            )
        )
    return db.session.scalars(stmt).all()


def set_user_active(actor, user, is_active):
    if not isinstance(is_active, bool):
        raise ApiError("is_active must be a boolean.", "VALIDATION_ERROR", 400)
    if user.id == actor.id:
        raise ApiError("You cannot deactivate your own account.", "VALIDATION_ERROR", 400)
    user.is_active = is_active
    db.session.commit()
    return user


def create_doctor(actor, data):
    """Create a DOCTOR user with its professional profile."""
    email = (data.get("email") or "").strip().lower()
    full_name = (data.get("full_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    license_no = (data.get("license_no") or "").strip()
    department_id = data.get("department_id")
    specialization = (data.get("specialization") or "").strip()
    experience_years = data.get("experience_years", 0)

    if not (email and "@" in email and "." in email):
        raise ApiError("A valid email is required.", "VALIDATION_ERROR", 400)
    if not full_name:
        raise ApiError("Full name is required.", "VALIDATION_ERROR", 400)
    if len(password) < 8:
        raise ApiError("Password must be at least 8 characters.", "VALIDATION_ERROR", 400)

    if db.session.scalar(db.select(User).where(User.email == email)):
        raise ApiError("A user with this email already exists.", "CONFLICT", 409)

    department = db.session.get(Department, department_id)
    if department is None or not department.is_active:
        raise ApiError("Unknown or inactive department_id.", "VALIDATION_ERROR", 400)
    try:
        experience_years = int(experience_years)
        if experience_years < 0:
            raise ValueError
    except (TypeError, ValueError):
        raise ApiError("experience_years must be a non-negative integer.", "VALIDATION_ERROR", 400)

    user = User(email=email, full_name=full_name, role=UserRole.DOCTOR, phone=phone)
    user.set_password(password)
    doctor = Doctor(
        user=user,
        department_id=department.id,
        license_no=license_no or None,
        specialization=specialization or None,
        experience_years=experience_years,
    )
    db.session.add(user)
    db.session.add(doctor)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("License number is already in use by another doctor.", "CONFLICT", 409)

    notification_service.notify(
        user, "account",
        "Welcome to AYUConnect",
        f"Dr. {full_name}, your doctor account is ready.",
        "/doctor/dashboard",
        commit=False,
    )
    db.session.commit()
    return user


def update_doctor(actor, doctor_id, data):
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None:
        raise ApiError("Doctor not found.", "NOT_FOUND", 404)
    for field in VALID_DOCTOR_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if field == "department_id":
            department = db.session.get(Department, value)
            if department is None or not department.is_active:
                raise ApiError("Unknown or inactive department_id.", "VALIDATION_ERROR", 400)
            doctor.department_id = department.id
        elif field == "experience_years":
            try:
                doctor.experience_years = int(value)
            except (TypeError, ValueError):
                raise ApiError("experience_years must be an integer.", "VALIDATION_ERROR", 400)
        elif field == "is_available":
            if not isinstance(value, bool):
                raise ApiError("is_available must be a boolean.", "VALIDATION_ERROR", 400)
            doctor.is_available = value
        else:
            setattr(doctor, field, (value or "").strip() if isinstance(value, str) else value)
    db.session.commit()
    return doctor


def list_audit_logs(limit=100):
    return db.session.scalars(
        db.select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    ).all()


def user_admin_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "phone": user.phone,
        "is_active": user.is_active,
        "created_at": (
            user.created_at.replace(tzinfo=None).isoformat()
            if user.created_at
            else None
        ),
    }


def audit_payload(entry):
    user = entry.user
    return {
        "id": entry.id,
        "user_email": user.email if user else None,
        "user_name": user.full_name if user else None,
        "action": entry.action,
        "resource": entry.resource,
        "resource_id": entry.resource_id,
        "ip_address": entry.ip_address,
        "details": entry.details,
        "created_at": (
            entry.created_at.replace(tzinfo=None).isoformat()
            if entry.created_at
            else None
        ),
    }
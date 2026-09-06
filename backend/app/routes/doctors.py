"""Doctors blueprint: public search, profiles, and availability."""

from flask import Blueprint, request

from ..extensions import db
from ..models import Department, Doctor, User
from ..services.serializers import (
    doctor_card_payload,
    doctor_detail_payload,
    slot_payload,
)
from ..utils.response import ApiError, api_success

doctors_bp = Blueprint("doctors", __name__, url_prefix="/api/doctors")


def _active_doctor_or_404(doctor_id):
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None or doctor.user is None or not doctor.user.is_active:
        raise ApiError("Doctor not found.", "NOT_FOUND", 404)
    return doctor


@doctors_bp.get("")
def list_doctors():
    """Search doctors. Filters: ``department`` (slug), ``q``, ``available``."""
    department_slug = (request.args.get("department") or "").strip().lower()
    query = (request.args.get("q") or "").strip()
    available_only = (request.args.get("available") or "").lower() in ("1", "true")

    stmt = (
        db.select(Doctor)
        .join(User, User.id == Doctor.user_id)
        .where(User.is_active.is_(True))
    )
    if department_slug:
        stmt = (
            stmt.join(Department, Department.id == Doctor.department_id)
            .where(db.func.lower(Department.slug) == department_slug)
        )
    if query:
        pattern = f"%{query.lower()}%"
        stmt = stmt.where(
            db.or_(
                db.func.lower(User.full_name).like(pattern),
                db.func.lower(Doctor.specialization).like(pattern),
            )
        )
    if available_only:
        stmt = stmt.where(Doctor.is_available.is_(True))

    stmt = stmt.order_by(Doctor.rating.desc(), User.full_name.asc())

    doctors = [doctor_card_payload(d) for d in db.session.scalars(stmt).all()]
    return api_success("Doctors", {"doctors": doctors, "count": len(doctors)})


@doctors_bp.get("/<int:doctor_id>")
def doctor_detail(doctor_id):
    """Public doctor profile including active weekly availability."""
    doctor = _active_doctor_or_404(doctor_id)
    return api_success("Doctor", {"doctor": doctor_detail_payload(doctor)})


@doctors_bp.get("/<int:doctor_id>/availability")
def doctor_availability(doctor_id):
    """Active availability slots for a doctor."""
    doctor = _active_doctor_or_404(doctor_id)
    slots = sorted(doctor.availability, key=lambda s: (s.weekday, s.start_time))
    return api_success(
        "Availability",
        {"doctor_id": doctor.id, "availability": [slot_payload(s) for s in slots if s.is_active]},
    )
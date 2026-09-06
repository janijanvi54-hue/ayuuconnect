"""Departments blueprint: public catalog browsing."""

from flask import Blueprint

from ..extensions import db
from ..models import Doctor
from ..services.serializers import (
    department_by_id_or_404,
    department_payload,
    doctor_card_payload,
    list_active_departments,
)
from ..utils.response import ApiError, api_success

departments_bp = Blueprint("departments", __name__, url_prefix="/api/departments")


@departments_bp.get("")
def list_departments():
    """List active departments with their available doctor counts."""
    departments = list_active_departments()
    data = [department_payload(d, doctor_count=len(d.doctors)) for d in departments]
    return api_success("Departments", {"departments": data})


@departments_bp.get("/<int:department_id>")
def department_detail(department_id):
    """Return a single active department."""
    department = department_by_id_or_404(department_id)
    return api_success(
        "Department", {"department": department_payload(department, doctor_count=len(department.doctors))}
    )


@departments_bp.get("/<int:department_id>/doctors")
def department_doctors(department_id):
    """List currently available doctors in an active department."""
    department = department_by_id_or_404(department_id)
    doctors = db.session.scalars(
        db.select(Doctor)
        .where(
            Doctor.department_id == department.id,
            Doctor.is_available.is_(True),
            Doctor.user.has(is_active=True),
        )
        .order_by(Doctor.rating.desc())
    ).all()
    return api_success(
        "Doctors",
        {"department": department_payload(department), "doctors": [doctor_card_payload(d) for d in doctors]},
    )
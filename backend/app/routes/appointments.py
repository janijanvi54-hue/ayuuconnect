"""Appointment routing: patient booking, public free slots, doctor status."""

from flask import Blueprint, request

from ..extensions import db
from ..models import Appointment, Doctor
from ..services import appointment_service, audit_service, notification_service
from ..services.serializers import appointment_payload
from ..utils.decorators import current_user, roles_required
from ..utils.response import ApiError, api_success

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api")


@appointments_bp.get("/doctors/<int:doctor_id>/slots")
def free_slots(doctor_id):
    """Free booking windows for a doctor on a concrete date."""
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None or doctor.user is None or not doctor.user.is_active:
        raise ApiError("Doctor not found.", "NOT_FOUND", 404)
    target = request.args.get("date") or ""
    result = appointment_service.doctor_slots_on_date(doctor, target)
    return api_success("Free slots", result)


@appointments_bp.get("/patients/appointments")
@roles_required("PATIENT")
def list_patient_appointments():
    patient = current_user().patient
    rows = db.session.scalars(
        db.select(Appointment)
        .where(Appointment.patient_id == patient.id)
        .order_by(Appointment.date.desc(), Appointment.start_time.desc())
    ).all()
    return api_success(
        "Appointments",
        {"appointments": [appointment_payload(a) for a in rows], "count": len(rows)},
    )


@appointments_bp.post("/patients/appointments")
@roles_required("PATIENT")
def book_appointment():
    patient = current_user().patient
    appointment, slot, doctor = appointment_service.book_appointment(
        patient, request.get_json(silent=True) or {}
    )
    notification_service.notify(
        doctor.user, "appointment",
        "New appointment request",
        f"{current_user().full_name} requested {appointment.date.isoformat()} "
        f"at {appointment.start_time.strftime('%H:%M')}.",
        "/doctor/appointments",
        commit=False,
    )
    audit_service.record_action(
        current_user(), "APPOINTMENT_CREATED", "appointment", appointment.id,
        {"date": appointment.date.isoformat(), "doctor_id": doctor.id},
    )
    db.session.commit()
    return api_success(
        "Appointment requested.",
        {"appointment": appointment_payload(appointment)},
        status=201,
    )


@appointments_bp.patch("/patients/appointments/<int:appointment_id>/cancel")
@roles_required("PATIENT")
def cancel_appointment(appointment_id):
    patient = current_user().patient
    appointment = appointment_service.cancel_appointment(patient, appointment_id)
    notification_service.notify(
        appointment.doctor.user, "appointment",
        "Appointment cancelled",
        f"{current_user().full_name} cancelled {appointment.date.isoformat()} "
        f"at {appointment.start_time.strftime('%H:%M')}.",
        "/doctor/appointments",
        commit=False,
    )
    audit_service.record_action(
        current_user(), "APPOINTMENT_CANCELLED", "appointment", appointment.id
    )
    db.session.commit()
    return api_success(
        "Appointment cancelled.", {"appointment": appointment_payload(appointment)}
    )
"""Appointment booking and status management."""

import datetime as dt

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import (
    Appointment,
    AppointmentStatus,
    Doctor,
    DoctorAvailability,
    PatientCase,
    CaseStatus,
)
from ..utils.response import ApiError

BOOKED_STATUSES = (
    AppointmentStatus.PENDING,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.COMPLETED,
)

VALID_TRANSITIONS = {
    AppointmentStatus.PENDING: {AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED,
                                AppointmentStatus.NO_SHOW},
    AppointmentStatus.CONFIRMED: {AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW,
                                  AppointmentStatus.CANCELLED},
    AppointmentStatus.COMPLETED: set(),
    AppointmentStatus.CANCELLED: set(),
    AppointmentStatus.NO_SHOW: set(),
}

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _parse_date(value, field="date"):
    try:
        return dt.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(f"{field} must be a YYYY-MM-DD date.", "VALIDATION_ERROR", 400)


def _parse_hhmm(value):
    try:
        return dt.time.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError("start_time must be an HH:MM time.", "VALIDATION_ERROR", 400)


def doctor_slots_on_date(doctor, target_date):
    """Free start times for ``doctor`` on ``target_date`` (no past dates)."""
    target_date = _parse_date(str(target_date))
    if target_date < dt.date.today():
        return {"slots": [], "doctor_id": doctor.id, "date": target_date.isoformat()}

    weekday = target_date.weekday()
    templates = [
        s for s in doctor.availability
        if s.is_active and s.weekday == weekday
    ]
    if not templates:
        return {"slots": [], "doctor_id": doctor.id, "date": target_date.isoformat()}

    taken = {
        (a.start_time, a.end_time)
        for a in db.session.scalars(
            db.select(Appointment).where(
                Appointment.doctor_id == doctor.id,
                Appointment.date == target_date,
                Appointment.status.in_(BOOKED_STATUSES),
            )
        ).all()
    }
    slots = [
        {
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "weekday": weekday,
        }
        for s in sorted(templates, key=lambda x: x.start_time)
        if (s.start_time, s.end_time) not in taken
    ]
    return {"slots": slots, "doctor_id": doctor.id, "date": target_date.isoformat()}


def book_appointment(patient, data):
    """Validate and create a PENDING appointment; guards double booking."""
    try:
        doctor_id = int(data.get("doctor_id"))
    except (TypeError, ValueError):
        raise ApiError("doctor_id is required.", "VALIDATION_ERROR", 400)
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None or doctor.user is None or not doctor.user.is_active:
        raise ApiError("Doctor not found.", "NOT_FOUND", 404)

    target_date = _parse_date(data.get("date"))
    if target_date < dt.date.today():
        raise ApiError("Appointment date cannot be in the past.", "VALIDATION_ERROR", 400)
    start_time = _parse_hhmm(data.get("start_time"))

    weekday = target_date.weekday()
    slot = db.session.execute(
        db.select(DoctorAvailability).where(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.weekday == weekday,
            DoctorAvailability.start_time == start_time,
            DoctorAvailability.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if slot is None:
        raise ApiError(
            f"{start_time.strftime('%H:%M')} is not within the doctor's "
            f"availability for {WEEKDAY_NAMES[weekday]}.",
            "VALIDATION_ERROR",
            400,
        )

    overlap = db.session.scalar(
        db.select(func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor.id,
            Appointment.date == target_date,
            Appointment.status.in_(BOOKED_STATUSES),
            Appointment.start_time < slot.end_time,
            Appointment.end_time > start_time,
        )
    )
    if overlap:
        raise ApiError("That time is already booked.", "CONFLICT", 409)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        department_id=doctor.department_id,
        availability_id=slot.id,
        date=target_date,
        start_time=start_time,
        end_time=slot.end_time,
        status=AppointmentStatus.PENDING,
        notes=(data.get("notes") or "").strip()[:500] or None,
    )
    db.session.add(appointment)
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("That time is already booked.", "CONFLICT", 409)
    return appointment, slot, doctor


def cancel_appointment(patient, appointment_id):
    """Patient cancels an own PENDING/CONFIRMED appointment."""
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None or appointment.patient_id != patient.id:
        raise ApiError("Appointment not found.", "NOT_FOUND", 404)
    if appointment.status not in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED):
        raise ApiError(
            "Only pending or confirmed appointments can be cancelled.",
            "VALIDATION_ERROR",
            400,
        )
    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    return appointment


def update_status(doctor, appointment_id, new_status):
    """Doctor drives an appointment through its lifecycle states."""
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None or appointment.doctor_id != doctor.id:
        raise ApiError("Appointment not found.", "NOT_FOUND", 404)

    try:
        target = AppointmentStatus(str(new_status).strip().upper())
    except ValueError:
        raise ApiError(
            f"status must be one of {sorted(s.value for s in AppointmentStatus)}.",
            "VALIDATION_ERROR",
            400,
        )
    allowed = VALID_TRANSITIONS[appointment.status]
    if target not in allowed:
        raise ApiError(
            f"Cannot change status from {appointment.status.value} to {target.value}.",
            "VALIDATION_ERROR",
            400,
        )
    appointment.status = target
    db.session.commit()
    return appointment


def ensure_case_after_confirmation(patient, doctor):
    """Open an authorization case the first time an appointment is confirmed."""
    existing = db.session.scalar(
        db.select(PatientCase).where(
            PatientCase.patient_id == patient.id,
            PatientCase.doctor_id == doctor.id,
        )
    )
    if existing is None:
        db.session.add(
            PatientCase(
                patient_id=patient.id,
                doctor_id=doctor.id,
                department_id=doctor.department_id,
                status=CaseStatus.ACTIVE,
            )
        )
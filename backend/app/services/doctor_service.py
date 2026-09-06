"""Doctor back-office business logic."""

import datetime as dt

from sqlalchemy import distinct, func
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import (
    Appointment,
    AppointmentStatus,
    CaseStatus,
    DoctorAvailability,
    Followup,
    FollowupStatus,
    MedicalRecord,
    Patient,
    PatientCase,
)
from ..utils.response import ApiError
from .serializers import (
    case_summary_payload,
    followup_payload,
    patient_card_payload,
    record_payload,
)

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
OPEN_CASE_STATUSES = (CaseStatus.OPEN, CaseStatus.ACTIVE)


def _parse_hhmm(value, field):
    try:
        return dt.time.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(
            f"{field} must be an HH:MM time.", "VALIDATION_ERROR", 400
        )


def get_my_doctor_or_error(user):
    """Return the doctor row for an authenticated doctor user."""
    doctor = user.doctor
    if doctor is None:
        raise ApiError("Doctor profile not found.", "NOT_FOUND", 404)
    return doctor


def dashboard_stats(doctor):
    """Aggregate counts shown on the doctor dashboard."""
    today = dt.date.today()
    upcoming_statuses = (
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
    )

    total_patients = db.session.scalar(
        db.select(func.count(distinct(PatientCase.patient_id))).where(
            PatientCase.doctor_id == doctor.id
        )
    )
    active_cases = db.session.scalar(
        db.select(func.count(PatientCase.id)).where(
            PatientCase.doctor_id == doctor.id,
            PatientCase.status.in_(OPEN_CASE_STATUSES),
        )
    )
    total_records = db.session.scalar(
        db.select(func.count(MedicalRecord.id)).where(
            MedicalRecord.doctor_id == doctor.id
        )
    )
    upcoming_appointments = db.session.scalar(
        db.select(func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor.id,
            Appointment.date >= today,
            Appointment.status.in_(upcoming_statuses),
        )
    )
    pending_appointments = db.session.scalar(
        db.select(func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor.id,
            Appointment.status == AppointmentStatus.PENDING,
        )
    )
    scheduled_followups = db.session.scalar(
        db.select(func.count(Followup.id)).where(
            Followup.scheduled_date >= today,
            Followup.status == FollowupStatus.SCHEDULED,
        )
    )
    active_slots = db.session.scalar(
        db.select(func.count(DoctorAvailability.id)).where(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.is_active.is_(True),
        )
    )

    return {
        "total_patients": total_patients or 0,
        "active_cases": active_cases or 0,
        "total_records": total_records or 0,
        "upcoming_appointments": upcoming_appointments or 0,
        "pending_appointments": pending_appointments or 0,
        "scheduled_followups": scheduled_followups or 0,
        "active_slots": active_slots or 0,
        "rating": float(doctor.rating) if doctor.rating is not None else 0.0,
    }


def add_availability(doctor, data):
    """Create one weekly slot; reject full duplicates."""
    weekday, start, end = _validate_slot_data(data, require_all=True)
    slot = DoctorAvailability(
        doctor_id=doctor.id, weekday=weekday, start_time=start, end_time=end
    )
    try:
        db.session.add(slot)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("This availability slot already exists.", "CONFLICT", 409)
    return slot


def update_availability(doctor, slot_id, data):
    """Partially update an owned slot (weekday/times/is_active)."""
    slot = _owned_slot_or_404(doctor, slot_id)

    weekday, start, end = None, None, None
    if "weekday" in data or "start_time" in data or "end_time" in data:
        merged = {
            "weekday": data.get("weekday", slot.weekday),
            "start_time": data.get("start_time", slot.start_time.strftime("%H:%M")),
            "end_time": data.get("end_time", slot.end_time.strftime("%H:%M")),
        }
        weekday, start, end = _validate_slot_data(merged)

    if weekday is not None:
        slot.weekday = weekday
    if start is not None:
        slot.start_time = start
    if end is not None:
        slot.end_time = end

    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            raise ApiError("is_active must be a boolean.", "VALIDATION_ERROR", 400)
        slot.is_active = data["is_active"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("This availability slot already exists.", "CONFLICT", 409)
    return slot


def delete_availability(doctor, slot_id):
    """Soft-delete an owned slot so appointment references stay intact."""
    slot = _owned_slot_or_404(doctor, slot_id)
    slot.is_active = False
    db.session.commit()
    return slot


def _owned_slot_or_404(doctor, slot_id):
    slot = db.session.get(DoctorAvailability, slot_id)
    if slot is None or slot.doctor_id != doctor.id:
        raise ApiError("Availability slot not found.", "NOT_FOUND", 404)
    return slot


def _validate_slot_data(data, require_all=False):
    if require_all and any(data.get(k) is None for k in ("weekday", "start_time", "end_time")):
        raise ApiError(
            "weekday, start_time, and end_time are required.", "VALIDATION_ERROR", 400
        )
    try:
        weekday = int(data["weekday"])
    except (KeyError, TypeError, ValueError):
        raise ApiError(
            "weekday must be 0 (Monday) to 6 (Sunday).", "VALIDATION_ERROR", 400
        )
    if weekday < 0 or weekday > 6:
        raise ApiError(
            f"weekday must be 0 (Monday) to 6 (Sunday); weekday names: "
            f"{', '.join(WEEKDAY_NAMES)}.",
            "VALIDATION_ERROR",
            400,
        )
    start = _parse_hhmm(data.get("start_time"), "start_time")
    end = _parse_hhmm(data.get("end_time"), "end_time")
    if end <= start:
        raise ApiError("end_time must be after start_time.", "VALIDATION_ERROR", 400)
    return weekday, start, end


def list_doctor_patients(doctor):
    """Distinct patients with an active or historical case for this doctor."""
    case_rows = db.session.scalars(
        db.select(PatientCase)
        .join(Patient, Patient.id == PatientCase.patient_id)
        .where(PatientCase.doctor_id == doctor.id)
        .order_by(PatientCase.updated_at.desc())
    ).all()

    seen, patients = set(), []
    for patient_case in case_rows:
        if patient_case.patient_id in seen:
            continue
        seen.add(patient_case.patient_id)
        patient = patient_case.patient
        patients.append(
            {
                "patient": patient_card_payload(patient),
                "case": case_summary_payload(patient_case),
            }
        )
    return patients


def patient_history(doctor, patient):
    """All cases/records/prescriptions/follow-ups for an authorized patient."""
    cases = db.session.scalars(
        db.select(PatientCase)
        .where(PatientCase.doctor_id == doctor.id, PatientCase.patient_id == patient.id)
        .order_by(PatientCase.assigned_at.desc())
    ).all()
    if not cases:
        raise ApiError(
            "You do not have an active case for this patient.", "NOT_FOUND", 404
        )
    return [
        {
            "case": case_summary_payload(patient_case),
            "records": [
                record_payload(record)
                for record in sorted(
                    patient_case.records, key=lambda r: r.created_at
                )
            ],
            "followups": [
                followup_payload(followup)
                for followup in sorted(
                    patient_case.followups, key=lambda f: f.scheduled_date
                )
            ],
        }
        for patient_case in cases
    ]


def list_doctor_appointments(doctor, status_filter=None):
    """Upcoming/past appointments with an optional status filter."""
    stmt = db.select(Appointment).where(Appointment.doctor_id == doctor.id)
    if status_filter:
        valid = {s.value for s in AppointmentStatus}
        normalized = str(status_filter).strip().upper()
        if normalized not in valid:
            raise ApiError(
                f"status must be one of {sorted(valid)}.", "VALIDATION_ERROR", 400
            )
        stmt = stmt.where(Appointment.status == AppointmentStatus(normalized))
    stmt = stmt.order_by(Appointment.date.asc(), Appointment.start_time.asc())
    return db.session.scalars(stmt).all()
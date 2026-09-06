"""Doctor panel blueprint: dashboard, availability, patients, and records."""

from flask import Blueprint, request

from ..extensions import db
from ..models import Patient
from ..services import doctor_service
from ..services.serializers import (
    appointment_payload,
    patient_card_payload,
    slot_payload,
)
from ..utils.decorators import current_user, roles_required
from ..utils.response import api_success

doctors_panel_bp = Blueprint("doctors_panel", __name__, url_prefix="/api/doctor")


def _my_doctor():
    return doctor_service.get_my_doctor_or_error(current_user())


@doctors_panel_bp.get("/dashboard")
@roles_required("DOCTOR")
def doctor_dashboard():
    return api_success(
        "Dashboard", {"stats": doctor_service.dashboard_stats(_my_doctor())}
    )


@doctors_panel_bp.get("/availability")
@roles_required("DOCTOR")
def get_availability():
    doctor = _my_doctor()
    slots = sorted(doctor.availability, key=lambda s: (s.weekday, s.start_time))
    return api_success(
        "Availability", {"availability": [slot_payload(s) for s in slots]}
    )


@doctors_panel_bp.post("/availability")
@roles_required("DOCTOR")
def post_availability():
    doctor = _my_doctor()
    slot = doctor_service.add_availability(
        doctor, request.get_json(silent=True) or {}
    )
    return api_success("Slot added.", {"slot": slot_payload(slot)}, status=201)


@doctors_panel_bp.patch("/availability/<int:slot_id>")
@roles_required("DOCTOR")
def patch_availability(slot_id):
    doctor = _my_doctor()
    slot = doctor_service.update_availability(
        doctor, slot_id, request.get_json(silent=True) or {}
    )
    return api_success("Slot updated.", {"slot": slot_payload(slot)})


@doctors_panel_bp.delete("/availability/<int:slot_id>")
@roles_required("DOCTOR")
def delete_availability(slot_id):
    doctor = _my_doctor()
    slot = doctor_service.delete_availability(doctor, slot_id)
    return api_success("Slot deactivated.", {"slot": slot_payload(slot)})


@doctors_panel_bp.get("/patients")
@roles_required("DOCTOR")
def list_patients():
    doctor = _my_doctor()
    return api_success(
        "Patients", {"patients": doctor_service.list_doctor_patients(doctor)}
    )


@doctors_panel_bp.get("/patients/<int:patient_id>")
@roles_required("DOCTOR")
def patient_detail(patient_id):
    """Basic patient profile (case-gated)."""
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return api_success("Patient not found.", status=404)
    doctor = _my_doctor()
    doctor_service.patient_history(doctor, patient)
    return api_success(
        "Patient", {"patient": patient_card_payload(patient)}
    )


@doctors_panel_bp.get("/patients/<int:patient_id>/records")
@roles_required("DOCTOR")
def patient_records(patient_id):
    """Full clinical history: cases, records, prescriptions, follow-ups."""
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return api_success("Patient not found.", status=404)
    doctor = _my_doctor()
    history = doctor_service.patient_history(doctor, patient)
    return api_success(
        "Patient history",
        {"patient_id": patient.id, "history": history},
    )


@doctors_panel_bp.get("/appointments")
@roles_required("DOCTOR")
def list_appointments():
    doctor = _my_doctor()
    status_filter = (request.args.get("status") or "").strip()
    appointments = doctor_service.list_doctor_appointments(doctor, status_filter or None)
    return api_success(
        "Appointments",
        {
            "appointments": [appointment_payload(a) for a in appointments],
            "count": len(appointments),
        },
    )
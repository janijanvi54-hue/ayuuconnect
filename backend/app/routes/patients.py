"""Patient blueprint: own profile endpoints."""

from flask import Blueprint, request

from ..services.patient_service import update_patient
from ..services.serializers import patient_payload
from ..utils.decorators import current_user, roles_required
from ..utils.response import api_success

patients_bp = Blueprint("patients", __name__, url_prefix="/api/patients")


@patients_bp.get("/profile")
@roles_required("PATIENT")
def get_patient_profile():
    """Return the authenticated patient's profile."""
    return api_success("Patient profile", {"patient": patient_payload(current_user().patient)})


@patients_bp.put("/profile")
@roles_required("PATIENT")
def put_patient_profile():
    """Update the authenticated patient's profile fields."""
    patient = update_patient(current_user(), request.get_json(silent=True) or {})
    return api_success("Profile updated.", {"patient": patient_payload(patient)})
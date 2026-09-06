"""Patient profile business logic."""

import re
from datetime import date

from ..extensions import db
from ..models import Department, Gender
from ..utils.response import ApiError

PHONE_RE = re.compile(r"^[+\d][\d\s\-]{7,14}$")
BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"}
VALID_GENDERS = {member.value for member in Gender}


def _parse_date(value, field):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ApiError(f"{field} must be a valid date (YYYY-MM-DD).", "VALIDATION_ERROR", 400)


def update_patient(user, data):
    """Apply validated profile edits to a patient user. Returns the patient."""
    patient = user.patient

    full_name = data.get("full_name")
    if full_name is not None:
        full_name = str(full_name).strip()
        if not full_name:
            raise ApiError("Full name cannot be empty.", "VALIDATION_ERROR", 400)
        user.full_name = full_name

    phone = data.get("phone")
    if phone is not None:
        phone = str(phone).strip()
        if not PHONE_RE.match(phone):
            raise ApiError("A valid phone number is required.", "VALIDATION_ERROR", 400)
        user.phone = phone

    date_of_birth = data.get("date_of_birth")
    if date_of_birth is not None:
        dob = _parse_date(date_of_birth, "date_of_birth")
        if dob > date.today():
            raise ApiError("Date of birth cannot be in the future.", "VALIDATION_ERROR", 400)
        patient.date_of_birth = dob

    gender = data.get("gender")
    if gender is not None:
        normalized = str(gender).strip().upper()
        if normalized not in VALID_GENDERS:
            raise ApiError("gender must be MALE, FEMALE, or OTHER.", "VALIDATION_ERROR", 400)
        patient.gender = Gender(normalized)

    blood_group = data.get("blood_group")
    if blood_group is not None:
        normalized = str(blood_group).strip().upper() or "Unknown"
        if normalized not in BLOOD_GROUPS:
            raise ApiError("blood_group is not a recognized value.", "VALIDATION_ERROR", 400)
        patient.blood_group = normalized

    emergency_contact = data.get("emergency_contact")
    if emergency_contact is not None:
        normalized = str(emergency_contact).strip()
        if normalized and not PHONE_RE.match(normalized):
            raise ApiError("A valid emergency contact is required.", "VALIDATION_ERROR", 400)
        patient.emergency_contact = normalized or None

    address = data.get("address")
    if address is not None:
        patient.address = str(address).strip() or None

    department_id = data.get("department_id")
    if department_id is not None:
        department = db.session.get(Department, department_id)
        if department is None or not department.is_active:
            raise ApiError("Unknown department_id.", "VALIDATION_ERROR", 400)
        patient.department_id = department.id

    for consent_field in ("consent_records", "consent_ai"):
        value = data.get(consent_field)
        if value is not None:
            if not isinstance(value, bool):
                raise ApiError(f"{consent_field} must be a boolean.", "VALIDATION_ERROR", 400)
            setattr(patient, consent_field, value)

    db.session.commit()
    return patient
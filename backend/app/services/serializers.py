"""API payload serializers shared across blueprints."""

from ..extensions import db
from ..models import Department
from ..utils.response import ApiError


def department_payload(department, doctor_count=None):
    """Public department representation."""
    payload = {
        "id": department.id,
        "name": department.name,
        "slug": department.slug,
        "description": department.description,
        "services": department.services,
        "icon": department.icon,
        "is_active": department.is_active,
    }
    if doctor_count is not None:
        payload["doctor_count"] = doctor_count
    return payload


def doctor_card_payload(doctor):
    """Public doctor card (no license or clinical detail)."""
    department = doctor.department
    return {
        "id": doctor.id,
        "full_name": doctor.user.full_name if doctor.user else None,
        "specialization": doctor.specialization,
        "experience_years": doctor.experience_years,
        "rating": float(doctor.rating) if doctor.rating is not None else None,
        "is_available": doctor.is_available,
        "avatar_url": doctor.user.avatar_url if doctor.user else None,
        "bio": doctor.bio,
        "department": (
            _department_ref(department) if department is not None else None
        ),
    }


def doctor_detail_payload(doctor):
    """Public doctor detail: card plus a concise availability overview."""
    availability = [
        slot_payload(slot)
        for slot in sorted(doctor.availability, key=lambda s: (s.weekday, s.start_time))
        if slot.is_active
    ]
    payload = doctor_card_payload(doctor)
    payload["availability"] = availability
    return payload


def slot_payload(slot):
    """Availability slot: weekday 0=Monday..6=Sunday, HH:MM times."""
    return {
        "id": slot.id,
        "weekday": slot.weekday,
        "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"),
        "is_active": slot.is_active,
    }


def _department_ref(department):
    return {"id": department.id, "name": department.name, "slug": department.slug}


def patient_payload(patient):
    """Patient profile representation (role-scoped, includes consent flags)."""
    user = patient.user
    return {
        "id": patient.id,
        "full_name": user.full_name if user else None,
        "email": user.email if user else None,
        "phone": user.phone if user else None,
        "date_of_birth": (
            patient.date_of_birth.isoformat() if patient.date_of_birth else None
        ),
        "gender": patient.gender.value if patient.gender else None,
        "blood_group": patient.blood_group,
        "emergency_contact": patient.emergency_contact,
        "address": patient.address,
        "department_id": patient.department_id,
        "consent_records": patient.consent_records,
        "consent_ai": patient.consent_ai,
    }


def department_by_id_or_404(department_id):
    """Fetch an active department or raise a 404 ApiError."""
    department = db.session.get(Department, department_id)
    if department is None or not department.is_active:
        raise ApiError("Department not found.", "NOT_FOUND", 404)
    return department


def list_active_departments():
    """All active departments ordered by name."""
    return db.session.scalars(
        db.select(Department)
        .where(Department.is_active.is_(True))
        .order_by(Department.name)
    ).all()


def appointment_payload(appointment):
    """Appointment representation shared by doctor and patient views."""
    patient_user = appointment.patient.user if appointment.patient else None
    doctor_user = appointment.doctor.user if appointment.doctor else None
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "patient_name": patient_user.full_name if patient_user else None,
        "doctor_id": appointment.doctor_id,
        "doctor_name": doctor_user.full_name if doctor_user else None,
        "department": (
            _department_ref(appointment.department)
            if appointment.department is not None
            else None
        ),
        "date": appointment.date.isoformat(),
        "start_time": appointment.start_time.strftime("%H:%M"),
        "end_time": appointment.end_time.strftime("%H:%M"),
        "status": appointment.status.value,
        "notes": appointment.notes,
        "availability_id": appointment.availability_id,
    }


def patient_card_payload(patient):
    """Doctor-facing patient card (case-gated in the route)."""
    user = patient.user
    return {
        "id": patient.id,
        "full_name": user.full_name if user else None,
        "gender": patient.gender.value if patient.gender else None,
        "date_of_birth": (
            patient.date_of_birth.isoformat() if patient.date_of_birth else None
        ),
        "blood_group": patient.blood_group,
        "phone": user.phone if user else None,
        "emergency_contact": patient.emergency_contact,
        "address": patient.address,
        "department": (
            _department_ref(patient.department)
            if patient.department is not None
            else None
        ),
        "consent_records": patient.consent_records,
        "consent_ai": patient.consent_ai,
    }


def case_summary_payload(patient_case):
    """Case summary: authorization state plus linked-content counts."""
    return {
        "id": patient_case.id,
        "patient_id": patient_case.patient_id,
        "doctor_id": patient_case.doctor_id,
        "department": (
            _department_ref(patient_case.department)
            if patient_case.department is not None
            else None
        ),
        "status": patient_case.status.value,
        "assigned_at": (
            patient_case.assigned_at.replace(tzinfo=None).isoformat()
            if patient_case.assigned_at
            else None
        ),
        "updated_at": (
            patient_case.updated_at.replace(tzinfo=None).isoformat()
            if patient_case.updated_at
            else None
        ),
        "records_count": len(patient_case.records),
        "prescriptions_count": len(patient_case.prescriptions),
        "followups_count": len(patient_case.followups),
    }


def followup_payload(followup):
    return {
        "id": followup.id,
        "scheduled_date": (
            followup.scheduled_date.isoformat() if followup.scheduled_date else None
        ),
        "instructions": followup.instructions,
        "status": followup.status.value,
    }


def prescription_payload(prescription):
    return {
        "id": prescription.id,
        "record_id": prescription.record_id,
        "medicine": prescription.medicine,
        "dosage": prescription.dosage,
        "frequency": prescription.frequency,
        "duration": prescription.duration,
        "instructions": prescription.instructions,
        "created_at": (
            prescription.created_at.replace(tzinfo=None).isoformat()
            if prescription.created_at
            else None
        ),
    }


def record_payload(record):
    """Clinical record with its prescriptions attached."""
    prescriptions = sorted(
        record.prescriptions, key=lambda p: p.created_at
    )
    return {
        "id": record.id,
        "case_id": record.case_id,
        "record_type": record.record_type.value,
        "title": record.title,
        "content": record.content,
        "is_visible_to_patient": record.is_visible_to_patient,
        "created_at": (
            record.created_at.replace(tzinfo=None).isoformat()
            if record.created_at
            else None
        ),
        "prescriptions": [prescription_payload(p) for p in prescriptions],
    }
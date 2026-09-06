"""Recommendation engine.

``AI_PROVIDER=demo`` uses deterministic keyword heuristics so the full
request/response contract works without external API keys. Point
``AI_PROVIDER`` at a real service later while keeping this shape.
"""

from ..extensions import db
from ..models import Department, Recommendation
from ..utils.response import ApiError

# keyword -> (department slug, category)
_KEYWORD_MAP = [
    (("bloat", "digest", "gas", "acid", "vata", "pitta", "indigestion"),
     "ayurveda", "digestive_wellness"),
    (("sleep", "stress", "anxiety", "insomnia", "migraine", "headache"),
     "ayurveda", "stress_and_sleep"),
    (("skin", "rash", "eczema", "psoriasis", "acne", "allergy", "allergic"),
     "homeopathy", "skin_and_allergy"),
    (("immunity", "cold", "cough", "frequent", "weakness", "energy"),
     "homeopathy", "immunity_support"),
    (("diet", "weight", "nutrition", "food", "detox", "obesity"),
     "naturopathy", "diet_and_lifestyle"),
    (("joint", "bone", "arthritis", "pain", "back", "knee"),
     "unani", "pain_and_joints"),
    (("diabet", "bp", "blood pressure", "thyroid", "chronic"),
     "unani", "chronic_care"),
]


def _evaluate(text):
    lowered = (text or "").lower()
    for keywords, slug, category in _KEYWORD_MAP:
        if any(k in lowered for k in keywords):
            return slug, category
    return None, "general_health"


def create_recommendation(patient, text):
    """Run the demo engine and persist a recommendation."""
    text = (text or "").strip()
    if len(text) < 10:
        raise ApiError(
            "Describe your concern in at least a few words.", "VALIDATION_ERROR", 400
        )
    if not patient.consent_ai:
        raise ApiError(
            "You have not consented to AI recommendations. "
            "Enable consent_records to continue.",
            "CONFLICT",
            409,
        )

    slug, category = _evaluate(text)
    department = None
    if slug:
        department = db.session.scalar(
            db.select(Department).where(
                Department.slug == slug, Department.is_active.is_(True)
            )
        )
    if department is None:
        department = db.session.scalar(
            db.select(Department).where(Department.is_active.is_(True)).order_by(Department.name)
        )

    confidence = 0.87 if department else 0.5
    raw_response = {
        "department": department.name if department else "General health",
        "category": category,
        "rationale": (
            f"Signals in your description match {department.name} best "
            f"({category}). Book a consultation to confirm."
        ),
    }

    recommendation = Recommendation(
        patient_id=patient.id,
        department_id=department.id if department else None,
        category=category,
        confidence=confidence,
        input_text=text,
        raw_response=raw_response,
    )
    db.session.add(recommendation)
    db.session.commit()
    return recommendation


def list_recommendations(patient):
    return db.session.scalars(
        db.select(Recommendation)
        .where(Recommendation.patient_id == patient.id)
        .order_by(Recommendation.created_at.desc())
    ).all()


def recommendation_payload(recommendation):
    department = recommendation.department
    return {
        "id": recommendation.id,
        "category": recommendation.category,
        "confidence": recommendation.confidence,
        "department": (
            {
                "id": department.id,
                "name": department.name,
                "slug": department.slug,
            }
            if department is not None
            else None
        ),
        "raw_response": recommendation.raw_response,
        "created_at": (
            recommendation.created_at.replace(tzinfo=None).isoformat()
            if recommendation.created_at
            else None
        ),
    }
"""Check My Health Concern: AI recommendations for patients."""

from flask import Blueprint, request

from ..services import audit_service, notification_service, recommendation_service
from ..utils.decorators import current_user, roles_required
from ..utils.response import api_success

recommendations_bp = Blueprint(
    "recommendations", __name__, url_prefix="/api/patients/recommendations"
)


@recommendations_bp.post("")
@roles_required("PATIENT")
def create_recommendation():
    patient = current_user().patient
    text = (request.get_json(silent=True) or {}).get("concern") or ""
    recommendation = recommendation_service.create_recommendation(patient, text)
    detail = recommendation_service.recommendation_payload(recommendation)
    notification_service.notify(
        current_user(), "recommendation",
        "Your health recommendation is ready",
        f"Matched {detail['raw_response']['department']} with "
        f"{int((detail['confidence'] or 0) * 100)}% confidence.",
        "/patient/recommendations",
        commit=False,
    )
    audit_service.record_action(
        current_user(), "RECOMMENDATION_CREATED", "recommendation", recommendation.id
    )
    from ..extensions import db
    db.session.commit()
    return api_success("Recommendation generated.", {"recommendation": detail}, status=201)


@recommendations_bp.get("")
@roles_required("PATIENT")
def list_recommendations():
    patient = current_user().patient
    rows = recommendation_service.list_recommendations(patient)
    return api_success(
        "Recommendations",
        {"recommendations": [recommendation_service.recommendation_payload(r) for r in rows]},
    )
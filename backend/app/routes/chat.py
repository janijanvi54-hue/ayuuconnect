"""Chat assistant sessions and messages for patients."""

from flask import Blueprint, request

from ..services import audit_service, chatbot_service
from ..utils.decorators import current_user, roles_required
from ..utils.response import api_success

chat_bp = Blueprint("chat", __name__, url_prefix="/api/patients/chat")


@chat_bp.get("/sessions")
@roles_required("PATIENT")
def list_sessions():
    patient = current_user().patient
    sessions = chatbot_service.list_sessions(patient)
    return api_success(
        "Sessions",
        {"sessions": [chatbot_service.session_payload(s) for s in sessions]},
    )


@chat_bp.post("/sessions")
@roles_required("PATIENT")
def create_session():
    patient = current_user().patient
    title = (request.get_json(silent=True) or {}).get("title")
    session = chatbot_service.create_session(patient, title)
    audit_service.record_action(
        current_user(), "CHAT_SESSION_CREATED", "chat_session", session.id
    )
    from ..extensions import db
    db.session.commit()
    return api_success(
        "Session created.", {"session": chatbot_service.session_payload(session)}, status=201
    )


@chat_bp.get("/sessions/<int:session_id>")
@roles_required("PATIENT")
def get_session(session_id):
    patient = current_user().patient
    session = chatbot_service.get_owned_session(patient, session_id)
    return api_success(
        "Session",
        {"session": chatbot_service.session_payload(session, include_messages=True)},
    )


@chat_bp.post("/sessions/<int:session_id>/messages")
@roles_required("PATIENT")
def send_message(session_id):
    patient = current_user().patient
    session = chatbot_service.get_owned_session(patient, session_id)
    content = (request.get_json(silent=True) or {}).get("content") or ""
    user_msg, bot_msg = chatbot_service.send_message(patient, session, content)
    return api_success(
        "Reply generated",
        {
            "user_message": chatbot_service.message_payload(user_msg),
            "bot_message": chatbot_service.message_payload(bot_msg),
        },
    )
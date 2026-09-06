"""Demo chatbot engine: keyword replies so the API contract works end to end."""

from ..extensions import db
from ..models import ChatMessage, ChatSender, ChatSession
from ..utils.response import ApiError

_PROVIDER = "demo"


def _reply_for(text):
    t = (text or "").lower()
    if any(w in t for w in ("hi", "hello", "hey", "namaste")):
        return ("Namaste! I am YourCare assistant. I can help you find the right "
                "AYUSH department, book appointments, or answer health questions.")
    if any(w in t for w in ("book", "appointment", "visit", "schedule")):
        return ("You can book a consultation from the Appointments tab. Pick a "
                "doctor and a free slot, and I will confirm it with the clinic.")
    if any(w in t for w in ("bloat", "digest", "gas", "indigestion", "acid")):
        return ("Bloating and sluggish digestion often respond well to an "
                "Ayurvedic routine — warm water, light meals, and Triphala. I "
                "recommend a digestive assessment.")
    if any(w in t for w in ("sleep", "stress", "anxiety", "insomnia")):
        return ("Stress and poor sleep are commonly Vata/Pitta imbalances. Try a "
                "consistent bedtime and avoid screens. An Ayurveda consultation "
                "could help personalize herbs.")
    if any(w in t for w in ("skin", "rash", "eczema", "psoriasis", "acne")):
        return ("Chronic skin concerns are a strong fit for Homeopathy, which "
                "treats the underlying pattern rather than just symptoms.")
    if any(w in t for w in ("diet", "weight", "nutrition", "food")):
        return ("For diet and weight goals, Naturopathy emphasizes whole-food "
                "plans and lifestyle correction. Start with one meal change at a time.")
    if any(w in t for w in ("thank", "thanks")):
        return "You are most welcome. Stay healthy!"
    return ("Thank you for sharing. I’m a demo assistant right now — for a "
            "personalized plan, book a consultation or run Check My Health Concern.")


def create_session(patient, title=None):
    session = ChatSession(
        patient_id=patient.id, title=(title or "New conversation").strip()[:150]
    )
    db.session.add(session)
    db.session.commit()
    return session


def list_sessions(patient):
    return db.session.scalars(
        db.select(ChatSession)
        .where(ChatSession.patient_id == patient.id)
        .order_by(ChatSession.updated_at.desc())
    ).all()


def get_owned_session(patient, session_id):
    session = db.session.get(ChatSession, session_id)
    if session is None or session.patient_id != patient.id:
        raise ApiError("Chat session not found.", "NOT_FOUND", 404)
    return session


def send_message(patient, session, content):
    content = (content or "").strip()
    if not content:
        raise ApiError("Message cannot be empty.", "VALIDATION_ERROR", 400)

    user_msg = ChatMessage(session_id=session.id, sender=ChatSender.USER, content=content)
    bot_reply = _reply_for(content)
    bot_msg = ChatMessage(
        session_id=session.id,
        sender=ChatSender.BOT,
        content=bot_reply,
        provider=_PROVIDER,
    )
    if not session.title or session.title == "New conversation":
        session.title = content[:60]
    db.session.add_all([user_msg, bot_msg])
    db.session.commit()
    return user_msg, bot_msg


def message_payload(message):
    return {
        "id": message.id,
        "sender": message.sender.value,
        "content": message.content,
        "provider": message.provider,
        "created_at": (
            message.created_at.replace(tzinfo=None).isoformat()
            if message.created_at
            else None
        ),
    }


def session_payload(session, include_messages=False):
    payload = {
        "id": session.id,
        "title": session.title,
        "created_at": (
            session.created_at.replace(tzinfo=None).isoformat()
            if session.created_at
            else None
        ),
        "updated_at": (
            session.updated_at.replace(tzinfo=None).isoformat()
            if session.updated_at
            else None
        ),
    }
    if include_messages:
        payload["messages"] = [message_payload(m) for m in session.messages]
    return payload
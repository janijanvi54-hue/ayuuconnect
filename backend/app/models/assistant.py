"""AI assistant persistence: recommendations and chat history."""

from ..extensions import db
from .base import BigIntPK, TimestampMixin, utcnow
from .enums import ChatSender, enum_values


class Recommendation(db.Model):
    """A recorded department suggestion produced for a patient."""
    __tablename__ = "recommendations"
    __table_args__ = (db.Index("idx_reco_patient", "patient_id", "created_at"),)

    id = db.Column(BigIntPK, primary_key=True)
    patient_id = db.Column(
        db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    department_id = db.Column(db.ForeignKey("departments.id", ondelete="SET NULL"))
    category = db.Column(db.String(60))
    confidence = db.Column(db.Float)
    input_text = db.Column(db.Text, nullable=False)
    raw_response = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    patient = db.relationship("Patient", back_populates="recommendations")
    department = db.relationship("Department")

    def __repr__(self):
        return f"<Recommendation id={self.id} patient_id={self.patient_id}>"


class ChatSession(TimestampMixin, db.Model):
    """A patient's conversation thread with the assistant."""
    __tablename__ = "chat_sessions"

    id = db.Column(BigIntPK, primary_key=True)
    patient_id = db.Column(
        db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(150))

    patient = db.relationship("Patient", back_populates="chat_sessions")
    messages = db.relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChatMessage.created_at",
    )

    def __repr__(self):
        return f"<ChatSession id={self.id} patient_id={self.patient_id}>"


class ChatMessage(db.Model):
    """One turn inside a chat session (user or bot)."""
    __tablename__ = "chat_messages"
    __table_args__ = (db.Index("idx_msg_session", "session_id", "created_at"),)

    id = db.Column(BigIntPK, primary_key=True)
    session_id = db.Column(
        db.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    sender = db.Column(
        db.Enum(ChatSender, name="chat_sender", values_callable=enum_values),
        nullable=False,
    )
    content = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    session = db.relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage id={self.id} session_id={self.session_id}>"
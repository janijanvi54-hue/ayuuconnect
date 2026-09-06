"""AuditLog model. Never store passwords, tokens, or secret payloads here."""

from ..extensions import db
from .base import BigIntPK, utcnow


class AuditLog(db.Model):
    """Immutable audit trail of meaningful actions."""
    __tablename__ = "audit_logs"
    __table_args__ = (
        db.Index("idx_audit_user", "user_id", "created_at"),
        db.Index("idx_audit_action", "action", "created_at"),
    )

    id = db.Column(BigIntPK, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(60), nullable=False)
    resource = db.Column(db.String(60))
    resource_id = db.Column(db.String(64))
    ip_address = db.Column(db.String(45))
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog id={self.id} action={self.action!r}>"
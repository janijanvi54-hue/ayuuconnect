"""Notification model (in-app; email/SMS channels layered on later)."""

from ..extensions import db
from .base import BigIntPK, utcnow


class Notification(db.Model):
    """An in-app message addressed to a user."""
    __tablename__ = "notifications"
    __table_args__ = (db.Index("idx_notif_user", "user_id", "is_read", "created_at"),)

    id = db.Column(BigIntPK, primary_key=True)
    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification id={self.id} user_id={self.user_id} type={self.type!r}>"
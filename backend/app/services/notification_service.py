"""In-app notification helpers."""

from ..extensions import db
from ..models import Notification


def notify(user, type_, title, body=None, link=None, commit=True):
    """Create an in-app notification for ``user``."""
    notification = Notification(
        user_id=user.id, type=type_, title=title, body=body, link=link
    )
    db.session.add(notification)
    if commit:
        db.session.commit()
    return notification


def unread_count(user):
    return db.session.scalar(
        db.select(db.func.count(Notification.id)).where(
            Notification.user_id == user.id, Notification.is_read.is_(False)
        )
    ) or 0


def list_for(user, only_unread=False):
    stmt = db.select(Notification).where(Notification.user_id == user.id)
    if only_unread:
        stmt = stmt.where(Notification.is_read.is_(False))
    return db.session.scalars(
        stmt.order_by(Notification.created_at.desc()).limit(100)
    ).all()


def mark_read(user, notification_id):
    notification = db.session.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        return None
    notification.is_read = True
    db.session.commit()
    return notification


def mark_all_read(user):
    count = db.session.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read.is_(False)
    ).update({"is_read": True})
    db.session.commit()
    return count


def notification_payload(notification):
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "body": notification.body,
        "link": notification.link,
        "is_read": notification.is_read,
        "created_at": (
            notification.created_at.replace(tzinfo=None).isoformat()
            if notification.created_at
            else None
        ),
    }
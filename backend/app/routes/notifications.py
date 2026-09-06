"""Notifications for the authenticated user (any role)."""

from flask import Blueprint

from ..services import notification_service
from ..utils.decorators import current_user, roles_required
from ..utils.response import api_success

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/me/notifications")


@notifications_bp.get("")
@roles_required("PATIENT", "DOCTOR", "ADMIN")
def list_my_notifications():
    notifications = notification_service.list_for(current_user())
    return api_success(
        "Notifications",
        {
            "notifications": [
                notification_service.notification_payload(n) for n in notifications
            ],
            "unread_count": notification_service.unread_count(current_user()),
        },
    )


@notifications_bp.get("/unread-count")
@roles_required("PATIENT", "DOCTOR", "ADMIN")
def my_unread_count():
    return api_success(
        "Unread count", {"unread_count": notification_service.unread_count(current_user())}
    )


@notifications_bp.post("/<int:notification_id>/read")
@roles_required("PATIENT", "DOCTOR", "ADMIN")
def mark_read(notification_id):
    notification = notification_service.mark_read(current_user(), notification_id)
    if notification is None:
        from ..utils.response import ApiError
        raise ApiError("Notification not found.", "NOT_FOUND", 404)
    return api_success("Marked as read.", {"notification": notification_service.notification_payload(notification)})


@notifications_bp.post("/read-all")
@roles_required("PATIENT", "DOCTOR", "ADMIN")
def mark_all_read():
    count = notification_service.mark_all_read(current_user())
    return api_success("All notifications marked as read.", {"marked": count})
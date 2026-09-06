"""Audit trail helper used by services and routes."""

from flask import has_request_context, request

from ..extensions import db
from ..models import AuditLog


def record_action(user, action, resource=None, resource_id=None, details=None):
    """Insert an immutable audit row (no-op failures are still safe)."""
    ip = None
    if has_request_context():
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
    entry = AuditLog(
        user_id=user.id if user is not None else None,
        action=action,
        resource=resource,
        resource_id=str(resource_id) if resource_id is not None else None,
        ip_address=ip,
        details=details,
    )
    db.session.add(entry)
    db.session.flush()
    return entry
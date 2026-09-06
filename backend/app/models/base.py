"""Shared column types and mixins for the SQLAlchemy data models."""

from datetime import UTC, datetime

from ..extensions import db

# Auto-incrementing primary key: BIGINT on MySQL, plain INTEGER on SQLite so
# that autoincrement keeps working in local development.
BigIntPK = db.BigInteger().with_variant(db.Integer, "sqlite")


def utcnow():
    """Timezone-aware UTC timestamp.

    Values are stored as nanoseconds-agnostic DATETIME by stripping the
    offset for portability across MySQL DATETIME and SQLite.
    """
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    """``created_at``/``updated_at`` maintained by the application layer."""

    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
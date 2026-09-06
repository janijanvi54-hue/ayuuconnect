"""Attribute value types used by the data models.

Values match the MySQL ENUM definitions in ``database/schema.sql``. SQLAlchemy
renders these as ENUM on MySQL and VARCHAR with a CHECK constraint on SQLite.
"""

import enum


class UserRole(enum.Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class CaseStatus(enum.Enum):
    OPEN = "OPEN"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class AppointmentStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class RecordType(enum.Enum):
    INITIAL_ASSESSMENT = "INITIAL_ASSESSMENT"
    TREATMENT = "TREATMENT"
    FOLLOW_UP = "FOLLOW_UP"
    NOTE = "NOTE"
    OTHER = "OTHER"


class FollowupStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    DONE = "DONE"
    MISSED = "MISSED"


class ChatSender(enum.Enum):
    USER = "USER"
    BOT = "BOT"


def enum_values(enum_class):
    """Return native DB values for a Python enum (used with ``values_callable``)."""
    return [member.value for member in enum_class]
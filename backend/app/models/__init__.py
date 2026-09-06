"""SQLAlchemy ORM models (mirror of ``database/schema.sql``).

Importing this package registers every table with the metadata shared by
Flask-Migrate and ``db.create_all()``.
"""

from .appointment import Appointment
from .assistant import ChatMessage, ChatSession, Recommendation
from .audit import AuditLog
from .base import BigIntPK, TimestampMixin, utcnow
from .case import Followup, PatientCase
from .department import Department, ProblemCategory
from .enums import (
    AppointmentStatus,
    CaseStatus,
    ChatSender,
    FollowupStatus,
    Gender,
    RecordType,
    UserRole,
)
from .notification import Notification
from .people import Doctor, DoctorAvailability, Patient
from .record import MedicalRecord, Prescription
from .user import Admin, User

__all__ = [
    "Admin",
    "Appointment",
    "AppointmentStatus",
    "AuditLog",
    "BigIntPK",
    "CaseStatus",
    "ChatMessage",
    "ChatSender",
    "ChatSession",
    "Department",
    "Doctor",
    "DoctorAvailability",
    "Followup",
    "FollowupStatus",
    "Gender",
    "MedicalRecord",
    "Notification",
    "Patient",
    "PatientCase",
    "Prescription",
    "ProblemCategory",
    "Recommendation",
    "RecordType",
    "TimestampMixin",
    "User",
    "UserRole",
    "utcnow",
]
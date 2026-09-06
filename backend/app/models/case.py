"""PatientCase (authorization hub) and Followup models."""

from ..extensions import db
from .base import BigIntPK, TimestampMixin, utcnow
from .enums import CaseStatus, FollowupStatus, enum_values


class PatientCase(db.Model):
    """Grants a doctor access to a patient's history and clinical workflow."""
    __tablename__ = "patient_cases"
    __table_args__ = (
        db.UniqueConstraint("patient_id", "doctor_id", name="uq_case_patient_doctor"),
        db.Index("idx_cases_doctor", "doctor_id"),
        db.Index("idx_cases_patient", "patient_id"),
    )

    id = db.Column(BigIntPK, primary_key=True)
    patient_id = db.Column(
        db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    doctor_id = db.Column(
        db.ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False
    )
    department_id = db.Column(db.ForeignKey("departments.id", ondelete="SET NULL"))
    status = db.Column(
        db.Enum(CaseStatus, name="case_status", values_callable=enum_values),
        nullable=False,
        default=CaseStatus.OPEN,
    )
    assigned_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    patient = db.relationship("Patient", back_populates="cases")
    doctor = db.relationship("Doctor", back_populates="cases")
    department = db.relationship("Department")
    records = db.relationship(
        "MedicalRecord",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    prescriptions = db.relationship(
        "Prescription",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    followups = db.relationship(
        "Followup",
        back_populates="case",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (f"<PatientCase id={self.id} patient_id={self.patient_id} "
                f"doctor_id={self.doctor_id} status={self.status.value}>")


class Followup(TimestampMixin, db.Model):
    """Scheduled follow-up visit tied to a patient case."""
    __tablename__ = "followups"
    __table_args__ = (db.Index("idx_followups_date", "case_id", "scheduled_date"),)

    id = db.Column(BigIntPK, primary_key=True)
    case_id = db.Column(
        db.ForeignKey("patient_cases.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_date = db.Column(db.Date, nullable=False)
    instructions = db.Column(db.Text)
    status = db.Column(
        db.Enum(FollowupStatus, name="followup_status", values_callable=enum_values),
        nullable=False,
        default=FollowupStatus.SCHEDULED,
    )

    case = db.relationship("PatientCase", back_populates="followups")

    def __repr__(self):
        return f"<Followup id={self.id} case_id={self.case_id}>"
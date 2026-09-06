"""MedicalRecord and Prescription models (clinical content, doctor-only)."""

from ..extensions import db
from .base import BigIntPK, TimestampMixin, utcnow
from .enums import RecordType, enum_values


class MedicalRecord(TimestampMixin, db.Model):
    """Clinical note attached to a patient case."""
    __tablename__ = "medical_records"
    __table_args__ = (
        db.Index("idx_records_patient", "patient_id"),
        db.Index("idx_records_case", "case_id"),
        db.Index("idx_records_doctor", "doctor_id"),
    )

    id = db.Column(BigIntPK, primary_key=True)
    case_id = db.Column(
        db.ForeignKey("patient_cases.id", ondelete="CASCADE"), nullable=False
    )
    patient_id = db.Column(
        db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    doctor_id = db.Column(
        db.ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False
    )
    record_type = db.Column(
        db.Enum(RecordType, name="record_type", values_callable=enum_values),
        nullable=False,
        default=RecordType.NOTE,
    )
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_visible_to_patient = db.Column(db.Boolean, nullable=False, default=True)

    case = db.relationship("PatientCase", back_populates="records")
    patient = db.relationship("Patient", back_populates="medical_records")
    doctor = db.relationship("Doctor", back_populates="medical_records")
    prescriptions = db.relationship("Prescription", back_populates="record")

    def __repr__(self):
        return f"<MedicalRecord id={self.id} title={self.title!r}>"


class Prescription(db.Model):
    """One medicine/dosage line on a case (optionally linked to a record)."""
    __tablename__ = "prescriptions"

    id = db.Column(BigIntPK, primary_key=True)
    record_id = db.Column(
        db.ForeignKey("medical_records.id", ondelete="SET NULL"), nullable=True
    )
    case_id = db.Column(
        db.ForeignKey("patient_cases.id", ondelete="CASCADE"), nullable=False
    )
    medicine = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(120))
    frequency = db.Column(db.String(120))
    duration = db.Column(db.String(120))
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    record = db.relationship("MedicalRecord", back_populates="prescriptions")
    case = db.relationship("PatientCase", back_populates="prescriptions")

    def __repr__(self):
        return f"<Prescription id={self.id} medicine={self.medicine!r}>"
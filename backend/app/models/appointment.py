"""Appointment model."""

from ..extensions import db
from .base import BigIntPK, TimestampMixin
from .enums import AppointmentStatus, enum_values


class Appointment(TimestampMixin, db.Model):
    """A booked visit between a patient and a doctor."""
    __tablename__ = "appointments"
    __table_args__ = (
        db.UniqueConstraint(
            "doctor_id", "date", "start_time", name="uq_appointment_doctor_slot"
        ),
        db.Index("idx_appts_patient", "patient_id", "date"),
        db.Index("idx_appts_doctor", "doctor_id", "date"),
        db.Index("idx_appts_status", "status"),
    )

    id = db.Column(BigIntPK, primary_key=True)
    patient_id = db.Column(
        db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    doctor_id = db.Column(
        db.ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False
    )
    department_id = db.Column(db.ForeignKey("departments.id", ondelete="SET NULL"))
    availability_id = db.Column(
        db.ForeignKey("doctor_availability.id", ondelete="SET NULL")
    )
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(
        db.Enum(AppointmentStatus, name="appointment_status", values_callable=enum_values),
        nullable=False,
        default=AppointmentStatus.PENDING,
    )
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    department = db.relationship("Department")
    availability = db.relationship("DoctorAvailability")

    def __repr__(self):
        return (f"<Appointment id={self.id} patient_id={self.patient_id} "
                f"doctor_id={self.doctor_id} status={self.status.value}>")
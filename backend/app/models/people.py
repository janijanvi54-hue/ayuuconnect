"""Patient and Doctor role rows plus weekly availability slots."""

from decimal import Decimal

from ..extensions import db
from .base import BigIntPK, TimestampMixin
from .enums import Gender, enum_values


class Patient(TimestampMixin, db.Model):
    """1:1 extension of ``users`` holding patient demographics and consents."""
    __tablename__ = "patients"

    id = db.Column(BigIntPK, primary_key=True)
    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    department_id = db.Column(
        db.ForeignKey("departments.id", ondelete="SET NULL"), index=True
    )
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum(Gender, name="gender", values_callable=enum_values))
    blood_group = db.Column(db.String(8))
    emergency_contact = db.Column(db.String(20))
    address = db.Column(db.Text)
    consent_records = db.Column(db.Boolean, nullable=False, default=True)
    consent_ai = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", back_populates="patient", foreign_keys=[user_id])
    department = db.relationship("Department", back_populates="patients")
    appointments = db.relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )
    cases = db.relationship(
        "PatientCase", back_populates="patient", cascade="all, delete-orphan"
    )
    medical_records = db.relationship(
        "MedicalRecord", back_populates="patient", cascade="all, delete-orphan"
    )
    recommendations = db.relationship(
        "Recommendation", back_populates="patient", cascade="all, delete-orphan"
    )
    chat_sessions = db.relationship(
        "ChatSession", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Patient id={self.id} user_id={self.user_id}>"


class Doctor(TimestampMixin, db.Model):
    """1:1 extension of ``users`` holding professional details."""
    __tablename__ = "doctors"

    id = db.Column(BigIntPK, primary_key=True)
    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    department_id = db.Column(
        db.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    license_no = db.Column(db.String(60), unique=True)
    specialization = db.Column(db.String(120))
    bio = db.Column(db.Text)
    experience_years = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Numeric(3, 2), nullable=False, default=Decimal("0.00"))
    is_available = db.Column(db.Boolean, nullable=False, default=True, index=True)

    user = db.relationship("User", back_populates="doctor", foreign_keys=[user_id])
    department = db.relationship("Department", back_populates="doctors")
    availability = db.relationship(
        "DoctorAvailability",
        back_populates="doctor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    appointments = db.relationship("Appointment", back_populates="doctor")
    cases = db.relationship("PatientCase", back_populates="doctor")
    medical_records = db.relationship("MedicalRecord", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor id={self.id} user_id={self.user_id}>"


class DoctorAvailability(TimestampMixin, db.Model):
    """Weekly slot template: one row per repeating weekday window."""
    __tablename__ = "doctor_availability"
    __table_args__ = (
        db.UniqueConstraint(
            "doctor_id", "weekday", "start_time", "end_time", name="uq_availability"
        ),
        db.Index("idx_avail_weekday", "doctor_id", "weekday"),
    )

    id = db.Column(BigIntPK, primary_key=True)
    doctor_id = db.Column(
        db.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False
    )
    weekday = db.Column(db.Integer, nullable=False)  # Monday=0 ... Sunday=6
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    doctor = db.relationship("Doctor", back_populates="availability")

    def __repr__(self):
        return (f"<DoctorAvailability id={self.id} doctor_id={self.doctor_id} "
                f"weekday={self.weekday}>")
"""Department and ProblemCategory models.

Departments are the AYUSH service lines; problem categories configure the
rule-based part of the AI department-suggestion engine.
"""

from ..extensions import db
from .base import BigIntPK, TimestampMixin


class Department(TimestampMixin, db.Model):
    """AYUSH service line (Ayurveda, Homeopathy, Unani, Yoga, ...)."""
    __tablename__ = "departments"

    id = db.Column(BigIntPK, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    services = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    doctors = db.relationship("Doctor", back_populates="department")
    patients = db.relationship("Patient", back_populates="department")

    def __repr__(self):
        return f"<Department id={self.id} name={self.name!r}>"


class ProblemCategory(TimestampMixin, db.Model):
    """Rule mapping: a problem keyword set to a suggested department."""
    __tablename__ = "problem_categories"

    id = db.Column(BigIntPK, primary_key=True)
    key = db.Column(db.String(60), nullable=False, unique=True)
    label = db.Column(db.String(120), nullable=False)
    keywords = db.Column(db.Text)
    default_department_id = db.Column(
        db.ForeignKey("departments.id", ondelete="SET NULL")
    )
    min_confidence = db.Column(db.Float)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    default_department = db.relationship("Department")

    def __repr__(self):
        return f"<ProblemCategory id={self.id} key={self.key!r}>"
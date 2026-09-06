"""User and Admin models (role extension rows are 1:1 with ``users``)."""

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .base import BigIntPK, TimestampMixin
from .enums import UserRole, enum_values


class User(TimestampMixin, db.Model):
    """Application account. Role-specific rows extend it in a 1:1 table."""
    __tablename__ = "users"
    __table_args__ = (
        db.Index("idx_users_role", "role"),
        db.Index("idx_users_created", "created_at"),
    )

    id = db.Column(BigIntPK, primary_key=True)
    email = db.Column(db.String(190), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(
        db.Enum(UserRole, name="user_role", values_callable=enum_values),
        nullable=False,
    )
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    patient = db.relationship(
        "Patient", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    doctor = db.relationship(
        "Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    admin = db.relationship(
        "Admin", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = db.relationship("AuditLog", back_populates="user")

    def set_password(self, password):
        """Hash and store ``password``. Never store plaintext."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Return True when ``password`` matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def identity(self):
        """Role-scope lookup helpers used later by the API auth layer."""
        return {
            UserRole.PATIENT: self.patient,
            UserRole.DOCTOR: self.doctor,
            UserRole.ADMIN: self.admin,
        }.get(self.role)

    def __repr__(self):
        role = self.role.value if self.role else None
        return f"<User id={self.id} email={self.email!r} role={role}>"


class Admin(TimestampMixin, db.Model):
    """Root/support accounts. Thin 1:1 extension of ``users``."""
    __tablename__ = "admins"

    id = db.Column(BigIntPK, primary_key=True)
    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    user = db.relationship("User", back_populates="admin", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Admin id={self.id} user_id={self.user_id}>"
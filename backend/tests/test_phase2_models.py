"""Phase 2 tests: ORM models, integrity constraints, and seed-demo."""

import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.cli import seed_demo_command
from app.extensions import db
from app.models import (
    Admin,
    Appointment,
    AppointmentStatus,
    AuditLog,
    CaseStatus,
    ChatMessage,
    ChatSender,
    Department,
    Doctor,
    DoctorAvailability,
    FollowupStatus,
    Gender,
    MedicalRecord,
    Notification,
    Patient,
    PatientCase,
    Prescription,
    Recommendation,
    User,
    UserRole,
)


def _user(email, full_name="Test User", role=UserRole.PATIENT):
    """Create a User with a valid password hash."""
    user = User(email=email, full_name=full_name, role=role)
    user.set_password("TestPass@123")
    db.session.add(user)
    return user


def _make_doctor(department, **kwargs):
    user = User(email="doc@example.test", full_name="Dr. Test", role=UserRole.DOCTOR)
    user.set_password("Secret@123")
    db.session.add(user)
    doctor = Doctor(
        user=user,
        department=department,
        license_no=kwargs.pop("license_no", "AYUSH-TEST-0001"),
        **kwargs,
    )
    db.session.add(doctor)
    return doctor


def test_tables_are_created(app):
    expected = {
        "users",
        "patients",
        "doctors",
        "admins",
        "departments",
        "doctor_availability",
        "patient_cases",
        "appointments",
        "medical_records",
        "prescriptions",
        "followups",
        "recommendations",
        "chat_sessions",
        "chat_messages",
        "notifications",
        "audit_logs",
        "problem_categories",
    }
    actual = set(db.metadata.tables)
    assert expected <= actual


def test_password_hash_roundtrip(app_ctx):
    user = User(email="hash@example.test", full_name="Hash Test", role=UserRole.ADMIN)
    user.set_password("Sup3rSecret!")
    db.session.add(user)
    db.session.commit()

    assert user.password_hash != "Sup3rSecret!"
    assert user.check_password("Sup3rSecret!") is True
    assert user.check_password("wrong-password") is False


def test_duplicate_email_rejected(app_ctx):
    for i in range(2):
        _user(email="dupe@example.test", full_name=f"Dupe {i}")
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_unique_case_pair_rejected(app_ctx):
    dept = Department(name="Ayurveda", slug="ayurveda")
    db.session.add(dept)
    patient = Patient(user=_user(email="p@example.test"))
    db.session.add(patient)
    doctor = _make_doctor(dept)
    db.session.commit()

    db.session.add(PatientCase(patient=patient, doctor=doctor))
    db.session.add(PatientCase(patient=patient, doctor=doctor))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_role_extension_one_to_one(app_ctx):
    dept = Department(name="Homeopathy", slug="homeopathy")
    db.session.add(dept)
    user = _user(email="a@example.test", full_name="A", role=UserRole.DOCTOR)
    db.session.add(Doctor(user=user, department=dept))
    db.session.commit()

    from app.models import Doctor as DoctorModel

    assert user.doctor.user_id == user.id
    assert isinstance(db.session.get(DoctorModel, user.doctor.id).user, User)


def test_timestamps_populated(app_ctx):
    user = _user(email="ts@example.test", full_name="TS")
    db.session.commit()

    assert user.created_at is not None
    assert user.updated_at is not None


def test_cascade_delete_user_removes_patient_row(app_ctx):
    user = _user(email="del@example.test", full_name="Del")
    db.session.add(Patient(user=user))
    db.session.commit()
    patient_id = user.patient.id

    db.session.delete(user)
    db.session.commit()

    assert db.session.get(Patient, patient_id) is None


def test_enum_values_are_stored(app_ctx):
    patient = Patient(user=_user(email="g@example.test"), gender=Gender.FEMALE, blood_group="B+")
    db.session.add(patient)
    db.session.commit()

    loaded = db.session.get(Patient, patient.id)
    assert loaded.gender.value == "FEMALE"
    assert loaded.blood_group == "B+"


def test_seed_demo_creates_demo_data(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0, result.output

    patient_user = db.session.execute(
        db.select(User).filter_by(email="patient@example.test")
    ).scalar_one()

    assert db.session.query(User).count() == 4
    assert db.session.query(Department).count() == 4
    assert db.session.query(Patient).filter_by(
        user_id=patient_user.id
    ).one().consent_ai is True

    doctor = db.session.execute(
        db.select(Doctor).join(User).filter(User.email == "doctor@example.test")
    ).scalar_one()
    assert doctor.license_no == "AYUSH-AY-0001"
    assert len(doctor.availability) == 6
    assert doctor.rating == Decimal("4.80")

    admin = db.session.execute(
        db.select(Admin).join(User).filter(User.email == "admin@example.test")
    ).scalar_one()
    assert admin is not None

    case = db.session.query(PatientCase).one()
    assert case.status == CaseStatus.ACTIVE
    assert len(case.records) == 1
    assert len(case.prescriptions) == 1
    assert len(case.followups) == 1
    assert case.followups[0].status == FollowupStatus.SCHEDULED

    appointment = db.session.query(Appointment).one()
    assert appointment.status == AppointmentStatus.CONFIRMED

    recommendation = db.session.query(Recommendation).one()
    assert recommendation.confidence == 0.92

    assert db.session.query(ChatMessage).count() == 2
    assert db.session.query(ChatMessage).filter_by(
        sender=ChatSender.BOT
    ).one().provider == "demo"

    assert db.session.query(Notification).count() == 3
    assert {log.action for log in db.session.query(AuditLog).all()} >= {"SEED_DEMO", "LOGIN"}


def test_seed_demo_is_idempotent(app):
    runner = app.test_cli_runner()
    first = runner.invoke(seed_demo_command)
    counts_after_first = {
        model.__name__: db.session.query(model).count()
        for model in (User, Department, Appointment, PatientCase, MedicalRecord, Prescription)
    }
    second = runner.invoke(seed_demo_command)
    assert first.exit_code == 0
    assert second.exit_code == 0

    for model in (User, Department, Appointment, PatientCase, MedicalRecord, Prescription):
        assert db.session.query(model).count() == counts_after_first[model.__name__]


def test_seed_demo_reset_flag(app):
    runner = app.test_cli_runner()
    runner.invoke(seed_demo_command)
    before = db.session.query(PatientCase).count()
    assert before == 1

    runner.invoke(seed_demo_command, args=["--reset"])
    # A reset wipes and reseeds exactly once: every relation is recreated.
    assert db.session.query(PatientCase).count() == 1
    assert db.session.query(User).count() == 4


def test_duplicate_availability_slot_rejected(app_ctx):
    dept = Department(name="Unani", slug="unani")
    db.session.add(dept)
    doctor = _make_doctor(dept)
    slot = dict(weekday=0, start_time=datetime.time(10, 0), end_time=datetime.time(11, 0))
    db.session.add(DoctorAvailability(doctor=doctor, **slot))
    db.session.add(DoctorAvailability(doctor=doctor, **slot))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
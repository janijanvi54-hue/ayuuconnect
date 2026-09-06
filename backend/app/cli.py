"""Flask CLI commands: development seeding.

``flask seed-demo`` is idempotent: running it twice changes nothing. Use
``--reset`` to drop and recreate all tables before seeding.
"""

from datetime import date, time, timedelta
from decimal import Decimal

import click
from flask.cli import with_appcontext

from .extensions import db
from .models import (
    Admin,
    Appointment,
    AppointmentStatus,
    AuditLog,
    CaseStatus,
    ChatMessage,
    ChatSender,
    ChatSession,
    Department,
    Doctor,
    DoctorAvailability,
    Followup,
    FollowupStatus,
    Gender,
    MedicalRecord,
    Notification,
    Patient,
    PatientCase,
    Prescription,
    Recommendation,
    RecordType,
    User,
    UserRole,
)

DEMO_PASSWORD = "DemoPass@123"

_DEPARTMENTS = [
    {
        "name": "Ayurveda",
        "slug": "ayurveda",
        "description": "Classical Indian system of medicine balancing the doshas.",
        "services": "Consultation, herbal medicine, Panchakarma, diet planning",
        "icon": "ayur",
    },
    {
        "name": "Homeopathy",
        "slug": "homeopathy",
        "description": "System based on the principle of 'like cures like'.",
        "services": "Consultation, constitutional remedies, acute care",
        "icon": "homo",
    },
    {
        "name": "Unani",
        "slug": "unani",
        "description": "Graeco-Arabic medicine focusing on the four humours.",
        "services": "Consultation, herbal remedies, regimental therapy",
        "icon": "unani",
    },
    {
        "name": "Yoga",
        "slug": "yoga",
        "description": "Holistic practice of asanas, pranayama, and lifestyle.",
        "services": "Therapy sessions, pranayama guidance, lifestyle coaching",
        "icon": "yoga",
    },
]


def _find(model, **filters):
    return db.session.execute(db.select(model).filter_by(**filters)).scalar_one_or_none()


def _demo_already_seeded():
    return _find(User, email="patient@example.test") is not None


def _seed_departments():
    """Create the department catalog (get-or-create, safe to re-run)."""
    departments = {}
    for data in _DEPARTMENTS:
        dept = _find(Department, slug=data["slug"])
        if dept is None:
            dept = Department(**data)
            db.session.add(dept)
            click.echo(f"  + department {data['name']}")
        else:
            click.echo(f"  = department {data['name']} (exists)")
        departments[data["slug"]] = dept
    return departments


def _seed_users(departments):
    """Create the three demo accounts plus a second doctor for richer data."""
    ayurveda = departments["ayurveda"]
    homeopathy = departments["homeopathy"]

    patient_user = User(
        email="patient@example.test",
        full_name="Priya Sharma",
        role=UserRole.PATIENT,
        phone="+91-98765-43210",
    )
    patient_user.set_password(DEMO_PASSWORD)
    db.session.add(patient_user)
    patient = Patient(
        user=patient_user,
        department=ayurveda,
        date_of_birth=date(1995, 6, 15),
        gender=Gender.FEMALE,
        blood_group="O+",
        emergency_contact="+91-91234-56789",
        address="14 Lake View Road, Pune",
        consent_records=True,
        consent_ai=True,
    )
    db.session.add(patient)

    doctor_user = User(
        email="doctor@example.test",
        full_name="Dr. Rajesh Verma",
        role=UserRole.DOCTOR,
        phone="+91-90000-00001",
    )
    doctor_user.set_password(DEMO_PASSWORD)
    db.session.add(doctor_user)
    doctor = Doctor(
        user=doctor_user,
        department=ayurveda,
        license_no="AYUSH-AY-0001",
        specialization="Panchakarma & Digestive Health",
        bio="Senior Ayurvedic physician with 12 years of clinical experience.",
        experience_years=12,
        rating=Decimal("4.80"),
        is_available=True,
    )
    db.session.add(doctor)
    for weekday in (0, 2, 4):
        db.session.add(
            DoctorAvailability(
                doctor=doctor, weekday=weekday, start_time=time(10, 0), end_time=time(13, 0)
            )
        )
        db.session.add(
            DoctorAvailability(
                doctor=doctor, weekday=weekday, start_time=time(16, 0), end_time=time(19, 0)
            )
        )

    second_doctor_user = User(
        email="second-doctor@example.test",
        full_name="Dr. Kavita Nair",
        role=UserRole.DOCTOR,
        phone="+91-90000-00002",
    )
    second_doctor_user.set_password(DEMO_PASSWORD)
    db.session.add(second_doctor_user)
    db.session.add(
        Doctor(
            user=second_doctor_user,
            department=homeopathy,
            license_no="AYUSH-HO-0002",
            specialization="Constitutional Homeopathy",
            bio="Specialist in constitutional homeopathy and chronic conditions.",
            experience_years=8,
            rating=Decimal("4.60"),
            is_available=True,
        )
    )

    admin_user = User(
        email="admin@example.test",
        full_name="Arogya Admin",
        role=UserRole.ADMIN,
        phone="+91-90000-00000",
    )
    admin_user.set_password(DEMO_PASSWORD)
    db.session.add(admin_user)
    db.session.add(Admin(user=admin_user))

    click.echo(f"  + users: patient@example.test, doctor@example.test, "
               f"second-doctor@example.test, admin@example.test")
    return patient_user, doctor, admin_user


def _seed_clinical(patient_user, doctor, admin_user, departments):
    """Sample appointment, case, record, prescription, follow-up, and AI data."""
    patient = patient_user.patient
    ayurveda = departments["ayurveda"]
    today = date.today()

    case = PatientCase(
        patient=patient,
        doctor=doctor,
        department=ayurveda,
        status=CaseStatus.ACTIVE,
    )
    db.session.add(case)

    appointment = Appointment(
        patient=patient,
        doctor=doctor,
        department=ayurveda,
        date=today + timedelta(days=3),
        start_time=time(10, 30),
        end_time=time(11, 15),
        status=AppointmentStatus.CONFIRMED,
        notes="First follow-up for the initial assessment.",
    )
    db.session.add(appointment)

    record = MedicalRecord(
        case=case,
        patient=patient,
        doctor=doctor,
        record_type=RecordType.INITIAL_ASSESSMENT,
        title="Initial assessment - digestive wellness",
        content=(
            "Patient reports bloating and low energy for about a month. "
            "Prakriti leans Vata-Pitta. Advised agni-balancing diet and "
            "evening walks; no contraindications noted."
        ),
        is_visible_to_patient=True,
    )
    db.session.add(record)

    db.session.add(
        Prescription(
            record=record,
            case=case,
            medicine="Ashwagandha Churna",
            dosage="3 g",
            frequency="Twice daily with warm water",
            duration="30 days",
            instructions="Take after meals; avoid on empty stomach.",
        )
    )
    followup_date = today + timedelta(days=14)
    db.session.add(
        Followup(
            case=case,
            scheduled_date=followup_date,
            instructions="Review response and adjust dosage.",
            status=FollowupStatus.SCHEDULED,
        )
    )

    db.session.add(
        Recommendation(
            patient=patient,
            department=ayurveda,
            category="digestive_wellness",
            confidence=0.92,
            input_text=(
                "Feeling bloated after meals for a month and low on energy."
            ),
            raw_response={
                "department": "Ayurveda",
                "rationale": "Bloating and low energy match Ayurveda's "
                             "apana-vayu imbalance pattern.",
            },
        )
    )

    session = ChatSession(patient=patient, title="Digestive concerns")
    db.session.add(session)
    db.session.add(
        ChatMessage(
            session=session,
            sender=ChatSender.USER,
            content="I have been feeling bloated after meals for about a month.",
        )
    )
    db.session.add(
        ChatMessage(
            session=session,
            sender=ChatSender.BOT,
            content=(
                "I would recommend an Ayurveda consultation. Your symptoms "
                "suggest a Vata-Pitta imbalance that responds well to "
                "agni-balancing diet and lifestyle changes."
            ),
            provider="demo",
        )
    )

    db.session.add_all(
        [
            Notification(
                user=patient_user,
                type="APPOINTMENT",
                title="Appointment confirmed",
                body="Your appointment with Dr. Rajesh Verma is confirmed.",
                link="/appointments",
            ),
            Notification(
                user=doctor.user,
                type="APPOINTMENT",
                title="New appointment booked",
                body="Priya Sharma has booked a consultation slot.",
                link="/appointments",
            ),
            Notification(
                user=patient_user,
                type="FOLLOWUP",
                title="Follow-up scheduled",
                body=f"Follow-up scheduled for {followup_date}.",
                link="/dashboard",
            ),
        ]
    )

    db.session.add_all(
        [
            AuditLog(
                user=admin_user, action="SEED_DEMO", resource="database",
                ip_address="127.0.0.1",
            ),
            AuditLog(
                user=patient_user, action="LOGIN", resource="auth",
                ip_address="127.0.0.1",
            ),
            AuditLog(
                user=doctor.user, action="LOGIN", resource="auth",
                ip_address="127.0.0.1",
            ),
        ]
    )

    click.echo("  + clinical: case, appointment, record, prescription, follow-up, "
               "recommendation, chat, notifications, audit logs")


@click.command("seed-demo")
@click.option("--reset", is_flag=True, help="Drop and recreate all tables first.")
@with_appcontext
def seed_demo_command(reset):
    """Seed department catalog, demo users, and sample clinical data."""
    if reset:
        db.drop_all()
        click.echo("Tables dropped.")
    db.create_all()
    if reset:
        click.echo("Database recreated.")
    elif not db.metadata.tables:
        click.echo("Database created.")

    if _demo_already_seeded():
        click.echo("Demo data already present. Run `flask seed-demo --reset` to reseed.")
        return

    departments = _seed_departments()
    patient_user, doctor, admin_user = _seed_users(departments)
    _seed_clinical(patient_user, doctor, admin_user, departments)

    db.session.commit()
    click.echo("Demo data seeded successfully.")
    click.echo("  Login: patient@example.test / doctor@example.test / "
               "admin@example.test  (password: DemoPass@123)")


def register_commands(app):
    """Register every CLI command with the Flask app."""
    app.cli.add_command(seed_demo_command)
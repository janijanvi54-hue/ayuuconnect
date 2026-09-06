"""Phase 5 tests: public doctor search, details, and availability."""
import datetime
from decimal import Decimal

from app.cli import seed_demo_command
from app.extensions import db
from app.models import Department, Doctor, DoctorAvailability, User, UserRole


def _seed(app):
    result = app.test_cli_runner().invoke(seed_demo_command)
    assert result.exit_code == 0


def test_list_doctors_all(client, app):
    _seed(app)
    response = client.get("/api/doctors")
    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["count"] == 2
    names = {d["full_name"] for d in body["doctors"]}
    assert names == {"Dr. Rajesh Verma", "Dr. Kavita Nair"}


def test_search_by_department_slug(client, app):
    _seed(app)
    response = client.get("/api/doctors?department=homeopathy")
    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["count"] == 1
    assert body["doctors"][0]["full_name"] == "Dr. Kavita Nair"


def test_search_by_query(client, app):
    _seed(app)
    response = client.get("/api/doctors?q=panchakarma")
    assert response.status_code == 200
    names = [d["full_name"] for d in response.get_json()["data"]["doctors"]]
    assert names == ["Dr. Rajesh Verma"]

    response = client.get("/api/doctors?q=kavita")
    names = [d["full_name"] for d in response.get_json()["data"]["doctors"]]
    assert names == ["Dr. Kavita Nair"]


def test_search_available_only(client, app):
    _seed(app)
    response = client.get("/api/doctors?available=true")
    assert response.get_json()["data"]["count"] == 2


def test_doctor_public_card_omits_license(client, app):
    _seed(app)
    rajesh = db.session.execute(
        db.select(Doctor).join(User).where(User.email == "doctor@example.test")
    ).scalar_one()
    card = client.get(f"/api/doctors/{rajesh.id}").get_json()["data"]["doctor"]
    assert card["full_name"] == "Dr. Rajesh Verma"
    assert card["rating"] == 4.8
    assert card["department"]["slug"] == "ayurveda"
    assert "license_no" not in card
    assert "availability" in card
    assert len(card["availability"]) == 6


def test_doctor_detail_404_for_missing(client):
    response = client.get("/api/doctors/99999")
    assert response.status_code == 404
    assert response.get_json()["error_code"] == "NOT_FOUND"


def test_doctor_availability_returns_active_slots(client, app):
    _seed(app)
    rajesh = db.session.execute(
        db.select(Doctor).join(User).where(User.email == "doctor@example.test")
    ).scalar_one()

    response = client.get(f"/api/doctors/{rajesh.id}/availability")
    assert response.status_code == 200
    slots = response.get_json()["data"]["availability"]
    assert len(slots) == 6
    mondays = [s for s in slots if s["weekday"] == 0]
    assert [s["start_time"] for s in mondays] == ["10:00", "16:00"]
    assert all(s["is_active"] for s in slots)


def test_inactive_availability_hidden(client, app):
    _seed(app)
    rajesh = db.session.execute(
        db.select(Doctor).join(User).where(User.email == "doctor@example.test")
    ).scalar_one()
    slot = rajesh.availability[0]
    slot.is_active = False
    db.session.commit()

    response = client.get(f"/api/doctors/{rajesh.id}/availability")
    slots = response.get_json()["data"]["availability"]
    assert all(s["id"] != slot.id for s in slots)


def test_private_extra_doctor_with_no_availability(client, app):
    _seed(app)
    doct = db.session.execute(
        db.select(Doctor).join(User).where(User.email == "doctor@example.test")
    ).scalar_one()
    response = client.get(f"/api/doctors/{doct.id}")
    assert response.status_code == 200


def test_doctor_order_by_rating(client, app):
    _seed(app)
    response = client.get("/api/doctors")
    ratings = [d["rating"] for d in response.get_json()["data"]["doctors"]]
    assert ratings == sorted(ratings, reverse=True)
"""Admin blueprint: dashboard, users, doctors, departments, audit."""

from flask import Blueprint, request

from ..extensions import db
from ..models import Department, User
from ..services import admin_service, audit_service, notification_service
from ..services.serializers import department_payload
from ..utils.decorators import current_user, roles_required
from ..utils.response import api_success

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/dashboard")
@roles_required("ADMIN")
def admin_dashboard():
    return api_success(
        "Dashboard", {"stats": admin_service.dashboard_stats()}
    )


@admin_bp.get("/users")
@roles_required("ADMIN")
def list_users():
    role = (request.args.get("role") or "").strip() or None
    query = (request.args.get("q") or "").strip() or None
    users = admin_service.list_users(role=role, query=query)
    return api_success(
        "Users",
        {"users": [admin_service.user_admin_payload(u) for u in users]},
    )


@admin_bp.patch("/users/<int:user_id>")
@roles_required("ADMIN")
def patch_user(user_id):
    actor = current_user()
    user = db.session.get(User, user_id)
    if user is None:
        return api_success("User not found.", status=404)
    data = request.get_json(silent=True) or {}
    if "is_active" not in data:
        return api_success("Nothing to update.")
    updated = admin_service.set_user_active(actor, user, bool(data["is_active"]))
    notification_service.notify(
        updated, "account",
        "Account status changed",
        f"Your account was {'activated' if updated.is_active else 'deactivated'} by an administrator.",
        link=None,
        commit=False,
    )
    audit_service.record_action(
        actor, "USER_STATUS_CHANGED", "user", updated.id,
        {"is_active": updated.is_active},
    )
    db.session.commit()
    return api_success(
        "User updated.", {"user": admin_service.user_admin_payload(updated)}
    )


@admin_bp.get("/doctors")
@roles_required("ADMIN")
def list_doctors():
    from ..models import Doctor
    from ..services.serializers import doctor_card_payload
    doctors = db.session.scalars(
        db.select(Doctor).join(User).order_by(User.full_name.asc())
    ).all()
    return api_success(
        "Doctors",
        {"doctors": [doctor_card_payload(d) for d in doctors]},
    )


@admin_bp.post("/doctors")
@roles_required("ADMIN")
def create_doctor():
    actor = current_user()
    user = admin_service.create_doctor(actor, request.get_json(silent=True) or {})
    audit_service.record_action(
        actor, "DOCTOR_CREATED", "user", user.id, {"email": user.email}
    )
    db.session.commit()
    from ..services import admin_service as _admin
    return api_success(
        "Doctor account created.",
        {"user": _admin.user_admin_payload(user)},
        status=201,
    )


@admin_bp.patch("/doctors/<int:doctor_id>")
@roles_required("ADMIN")
def patch_doctor(doctor_id):
    actor = current_user()
    doctor = admin_service.update_doctor(actor, doctor_id, request.get_json(silent=True) or {})
    audit_service.record_action(
        actor, "DOCTOR_UPDATED", "doctor", doctor_id, {"is_available": doctor.is_available}
    )
    db.session.commit()
    from ..services.serializers import doctor_card_payload
    return api_success(
        "Doctor updated.", {"doctor": doctor_card_payload(doctor)}
    )


@admin_bp.get("/departments")
@roles_required("ADMIN")
def list_departments():
    departments = db.session.scalars(db.select(Department).order_by(Department.name)).all()
    return api_success(
        "Departments",
        {"departments": [department_payload(d) for d in departments]},
    )


@admin_bp.post("/departments")
@roles_required("ADMIN")
def create_department():
    actor = current_user()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    slug = (data.get("slug") or "").strip().lower() or name.lower().replace(" ", "-")
    if not name:
        from ..utils.response import ApiError
        raise ApiError("name is required.", "VALIDATION_ERROR", 400)
    department = Department(
        name=name,
        slug=slug,
        description=data.get("description"),
        services=data.get("services"),
        icon=data.get("icon"),
    )
    db.session.add(department)
    try:
        db.session.flush()
    except Exception:
        db.session.rollback()
        from ..utils.response import ApiError
        raise ApiError("A department with this slug already exists.", "CONFLICT", 409)
    audit_service.record_action(actor, "DEPARTMENT_CREATED", "department", department.id)
    db.session.commit()
    return api_success(
        "Department created.",
        {"department": department_payload(department)},
        status=201,
    )


@admin_bp.patch("/departments/<int:department_id>")
@roles_required("ADMIN")
def patch_department(department_id):
    actor = current_user()
    department = db.session.get(Department, department_id)
    if department is None:
        return api_success("Department not found.", status=404)
    data = request.get_json(silent=True) or {}
    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            from ..utils.response import ApiError
            raise ApiError("is_active must be a boolean.", "VALIDATION_ERROR", 400)
        department.is_active = data["is_active"]
    if "description" in data:
        department.description = data["description"]
    if "services" in data:
        department.services = data["services"]
    if "icon" in data:
        department.icon = data["icon"]
    db.session.commit()
    audit_service.record_action(actor, "DEPARTMENT_UPDATED", "department", department.id)
    return api_success(
        "Department updated.", {"department": department_payload(department)}
    )


@admin_bp.get("/audit-logs")
@roles_required("ADMIN")
def audit_logs():
    logs = admin_service.list_audit_logs()
    return api_success(
        "Audit logs",
        {"logs": [admin_service.audit_payload(entry) for entry in logs]},
    )
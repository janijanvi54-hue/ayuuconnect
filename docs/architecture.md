# AYUConnect – Architecture

**AYUConnect – AI-Enabled Integrated AYUSH Healthcare Management and Recommendation System**

## 1. Overview

AYUConnect is a responsive full-stack web application that connects patients, doctors/AYUSH
practitioners, and administrators. Patients describe a health concern in natural language and
receive an **AI-assisted department recommendation** (with a clear disclaimer that this is not a
diagnosis). They can explore AYUSH departments, find doctors, view availability, book
appointments, view authorized medical history, and chat with an AI healthcare assistant.

## 2. High-Level Architecture

```
Browser (React SPA)
      │  HTTPS / REST (JSON)
      ▼
Flask REST API (backend/app)
      │
      ├── Auth & RBAC (JWT, middleware)
      ├── Business Services (services/)
      │     ├── recommendation_service.py   (rule-based, AI-exchangeable)
      │     └── chatbot_service.py          (provider abstraction)
      ├── AI layer (ai/)
      │     ├── recommendation.py
      │     └── chatbot.py
      └── SQLAlchemy ORM
            │
            ▼
       MySQL (production) / SQLite (dev fallback)
```

The frontend is a **single responsive React application** used for desktop, tablet, and mobile.
There is no separate mobile application.

## 3. Technology Stack

| Layer      | Technology                                                            |
| ---------- | --------------------------------------------------------------------- |
| Frontend   | React 18, Vite, JavaScript, React Router, Axios, Bootstrap 5, Recharts |
| Backend    | Python 3.x, Flask (REST API), SQLAlchemy ORM, Flask-Migrate, Flask-CORS |
| Auth       | JWT (access tokens) + role-based access control, Werkzeug hashing      |
| Database   | MySQL 8 (production), SQLite (local fallback via `DATABASE_URL`)       |
| AI         | Transparent rule-based engine in demo mode; provider abstraction       |
| DevOps     | Docker Compose (frontend/backend/database), env-based config           |

## 4. Modular Backend Structure

```
backend/
├── app/
│   ├── __init__.py        # create_app() application factory
│   ├── config.py          # Base / Development / Testing / Production configs
│   ├── extensions.py      # SQLAlchemy, Migrate, JWTManager singletons
│   ├── models/            # SQLAlchemy models (users, patients, doctors, ...)
│   ├── routes/            # REST blueprints (auth, patient, doctor, admin, ...)
│   ├── services/          # business logic (recommendation, chatbot, notifications)
│   ├── middleware/        # auth + role guards, rate limiting
│   └── utils/             # helpers (response envelope, validation, audit)
├── migrations/            # Flask-Migrate revision history
├── tests/                 # pytest suite
├── requirements.txt
└── run.py                 # entry point
```

### Application factory

`create_app()` assembles configuration, extensions, CORS, blueprints, and error handlers.
Tests can create isolated app instances with a dedicated test config and in-memory SQLite.

## 5. Roles & Access Control

Three roles: `PATIENT`, `DOCTOR`, `ADMIN`.

- Backend enforces authorization on **every** protected endpoint via decorators
  (`@jwt_required`, `@role_required("DOCTOR")`) plus per-resource ownership checks.
- Frontend route guards improve UX only; they are never the security boundary.
- Admin has **operational** access only. Sensitive clinical data (records, assessments,
  prescriptions, private notes) is not exposed to admin APIs.

See `docs/api.md` for the endpoint matrix and `backend/app/middleware` for enforcement.

## 6. AI Safety

- The recommendation engine returns a **suggested department**, never a diagnosis.
- Standard disclaimer: “This is an AI-assisted department suggestion, not a diagnosis.”
- No prescription, no certainty claims, no emergency decisions.
- Urgent symptoms trigger a prompt to seek immediate professional/emergency care.
- Final clinical assessment is always performed by a qualified practitioner.

## 7. Environments

| Environment  | DB URL            | Debug | JWT cookie | CORS          | Seed accounts |
| ------------ | ----------------- | ----- | ---------- | ------------- | ------------- |
| development  | DATABASE_URL/env  | On    | Off        | localhost:5173| Yes (demo)    |
| testing      | sqlite memory     | Off   | Off        | test origin   | Test fixtures |
| production   | DATABASE_URL(env) | Off   | Secure     | explicit list | Never         |

Production requires `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, and `CORS_ORIGINS`
to be provided through the environment. Debug mode is always disabled.

## 8. Deployment Diagram

```
Vercel/Netlify (static)  ── React build (frontend/dist)
        │ HTTPS
        ▼
Render/Railway/Fly.io  ── Flask (run.py, Gunicorn)
        │
        ▼
Managed MySQL
```

See `README.md` → Deployment.

## 9. Future Extensibility

- `recommendation_service.py` and `chatbot_service.py` are thin abstractions; an ML/NLP
  backend can replace the rule engine / demo provider without API changes.
- The database design supports additional AYUSH departments, notification channels
  (email/SMS), and analytics.
- Frontend is a standard React SPA, compatible with future mobile shells.
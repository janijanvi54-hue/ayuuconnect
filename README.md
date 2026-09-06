# AYUConnect

**AYUConnect – AI-Enabled Integrated AYUSH Healthcare Management and Recommendation System**

AYUConnect is a responsive full-stack healthcare platform that connects **patients**,
**doctors/AYUSH practitioners**, and **administrators**. Patients describe a health concern
in natural language, receive an **AI-assisted department recommendation** (with a clear
disclaimer — never a diagnosis), find practitioners, book appointments, track authorized
medical history, and chat with an AI healthcare assistant.

---

## Features

### Patients
- Register / log in with role-based dashboards
- Personalized dashboard (upcoming appointment, recommended department, quick actions)
- "Check My Health Concern" → AI-assisted AYUSH department suggestion (demo rule engine)
- Explore departments (Ayurveda, Homeopathy, Unani, Yoga) and search doctors
- View doctor availability, book/cancel appointments (double-booking prevented)
- View own authorized medical/case history
- AI healthcare assistant (chatbot) — demo mode works without any API key

### Doctors
- Dashboard: today's / upcoming / pending appointments, patient count, availability
- Manage profile and weekly availability (no overlapping slots)
- View only **authorized** patients and their case history
- Manage appointments and add clinical records, prescriptions, and follow-ups

### Administrators
- Operational dashboard with statistics and charts
- Manage departments, doctors, users, appointments, and doctor assignment
- Generate operational reports
- **No access to sensitive clinical content** (enforced at the backend)

### Platform
- Responsive (desktop / tablet / mobile) single React app
- JWT auth + strict role-based access control on every protected API
- Audit logging, in-app notifications, normalized MySQL database
- Docker Compose development stack

---

## Safety

AYUConnect's AI **never claims to diagnose**. It provides:
- General AYUSH information and department guidance
- Appointment and healthcare navigation
- Educational material

Outputs are always accompanied by: *"This is an AI-assisted department suggestion, not a
diagnosis."* A qualified healthcare professional always makes the final clinical assessment.
In an emergency, users are directed to immediate professional/emergency care.

---

## Technology Stack

| Layer      | Technology                                                           |
| ---------- | -------------------------------------------------------------------- |
| Frontend   | React 18, Vite, JavaScript, React Router, Axios, Bootstrap 5, Recharts |
| Backend    | Python 3.x, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS        |
| Auth       | JWT (Flask-JWT-Extended) + Werkzeug password hashing                  |
| Database   | MySQL 8 (production), SQLite (local fallback)                         |
| AI         | Configurable provider — `demo` (default) or `external`                |
| DevOps     | Docker Compose, Gunicorn                                              |

---

## Architecture

```
Browser (React SPA)
      │  REST / JSON
      ▼
Flask API  ── middleware: JWT + RBAC
      │
      ├── services (recommendation_service, chatbot_service, ...)
      ├── ai/ (rule engine + chatbot provider abstraction)
      └── SQLAlchemy ORM ──► MySQL / SQLite
```

Full details: [`docs/architecture.md`](docs/architecture.md).

## Database

Normalized relational design with the main entities: users, patients, doctors, admins,
departments, doctor_availability, appointments, patient_cases, medical_records,
prescriptions, followups, recommendations, chat_sessions, chat_messages, notifications,
audit_logs, and problem_categories.

- Canonical MySQL DDL: [`database/schema.sql`](database/schema.sql)
- Reference seed data: [`database/seed.sql`](database/seed.sql)
- Design document: [`docs/database.md`](docs/database.md)

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- MySQL 8 (optional — SQLite is used automatically when `DATABASE_URL` is unset)

### 1. Clone and configure

```bash
cp .env.example .env        # then edit .env with your own values
```

`.env` is gitignored and must never be committed.

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Database setup

Local MySQL:
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p ayuconnect < database/seed.sql
```

**Or** run migrations + seed entirely through the app:

```bash
cd backend
export FLASK_APP=run.py            # PowerShell: $env:FLASK_APP="run.py"
flask db upgrade                   # creates tables from models
flask seed-demo                    # dev-only demo data + accounts
```

> When `DATABASE_URL` is left empty, development uses an auto-created
> `backend/ayuconnect_dev.db` SQLite file — no MySQL server required.

## Environment Variables

| Variable | Purpose | Default |
| -------- | ------- | ------- |
| `FLASK_ENV` | `development` / `testing` / `production` | `development` |
| `SECRET_KEY` | Flask signing secret | dev-only default |
| `JWT_SECRET_KEY` | JWT signing secret | dev-only default |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | Token lifetime | `720` |
| `DATABASE_URL` | SQLAlchemy URL (`mysql+pymysql://…` or `sqlite:///…`) | sqlite dev file |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `AI_PROVIDER` | `demo` or `external` | `demo` |
| `AI_API_KEY` | External AI key (never in frontend JS) | empty |
| `PORT` | Backend port | `5000` |
| `VITE_API_BASE_URL` | Frontend → API base URL | `/api` |

See [`.env.example`](.env.example).

## Running Backend

```bash
cd backend
python run.py          # development (debug on, SQLite/MySQL per .env)
```

Health check: `GET http://localhost:5000/api/health`

```bash
flask routes           # list all API routes
```

## Running Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173  (proxies /api → :5000)
```

Production build: `npm run build` → `frontend/dist`.

## Demo Accounts (development only)

| Role    | Email                | Password      |
| ------- | -------------------- | ------------- |
| Patient | `patient@example.test` | `DemoPass@123` |
| Doctor  | `doctor@example.test`  | `DemoPass@123` |
| Admin   | `admin@example.test`   | `DemoPass@123` |

Created by `flask seed-demo`. Never deploy these to production.

## API Documentation

REST API at `/api` with a consistent JSON envelope:

```json
{ "success": true, "message": "…", "data": {} }
{ "success": false, "message": "…", "error_code": "AUTH_FORBIDDEN" }
```

Featured endpoints:

```text
POST /api/auth/register          POST /api/auth/login
POST /api/patients/problem       POST /api/ai/recommend
POST /api/ai/chat
GET  /api/departments            GET  /api/doctors
POST /api/appointments           GET  /api/doctor/patients
GET  /api/admin/dashboard        GET  /api/admin/reports
```

Full reference + access-control matrix: [`docs/api.md`](docs/api.md).

## Testing

```bash
cd backend
python -m pytest tests -v
```

Coverage includes auth, authorization, patient/doctor/admin APIs, appointment booking,
double-booking prevention, availability, and the recommendation endpoint. Frontend
component tests are added alongside the corresponding pages.

## Docker

Requires Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:5000/api/health
- MySQL: localhost:3306 (credentials in `docker-compose.yml`, dev only)

Docker Compose architecture: `frontend (nginx) → backend (Flask) → database (MySQL)`.

> **Local dev machine note:** This developer machine runs Windows 10 build 19042, which is
> below Docker Desktop's minimum (22H2 / build 19045), so Docker Desktop cannot be installed
> here. Development proceeds fully on local Node + Python; the Docker configuration is kept
> as deployment-ready config and validated on a supported OS (or via Docker Engine inside
> WSL2 on a newer Windows build).

## Deployment

Recommended: static hosting for the frontend, a WSGI host for Flask, managed MySQL.

1. Build the frontend: `cd frontend && npm ci && npm run build` and deploy `dist/`.
2. Configure the backend environment (`FLASK_ENV=production`, real secrets, MySQL URL,
   restricted `CORS_ORIGINS`).
3. Create the production database: `mysql -u root -p < database/schema.sql`.
4. Run migrations: `flask db upgrade`.
5. **Do not** run `flask seed-demo` in production.
6. Deploy the backend with Gunicorn, e.g.
   `gunicorn --bind 0.0.0.0:8000 --workers 3 run:app`.
7. Point `VITE_API_BASE_URL` at the backend HTTPS origin and rebuild the frontend.
8. Verify CORS configuration, TLS termination, and the health endpoint.

Production disables debug mode and refuses to start without explicit secrets or with a
SQLite URL (`backend/app/config.py`).

## Security

- Passwords hashed with Werkzeug; no plaintext storage
- JWT auth + backend-enforced role-based authorization on every protected endpoint
- Input validation on the backend; SQL injection mitigated via SQLAlchemy parameterization
- Secrets from environment variables; no keys in frontend code
- Configurable CORS; audit logging of sensitive actions
- Admin role deliberately lacks access to clinical record contents
- Production: debug off, HTTPS expected, restricted CORS

## AI Limitations

- The recommendation engine is a transparent rule-based classifier (`AI_PROVIDER=demo`)
  designed so a real ML/NLP model can be swapped in later.
- The chatbot runs in `/api/ai/chat` with the same provider abstraction.
- AI outputs are suggestions for navigating care — **not** diagnosis, prescription,
  or emergency advice. A qualified practitioner always makes the final assessment.

## Development Phases

The project is built incrementally (structure → data model → auth → patient → doctor →
admin → appointments → recommendation → chatbot → notifications/audit → testing/security →
deployment). See [`docs/architecture.md`](docs/architecture.md) for the current status.

## License

For internal/educational use. Not a certified medical device.
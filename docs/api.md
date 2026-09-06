# AYUConnect – API Reference

Base URL (development): `http://localhost:5000/api`

All endpoints return the standard envelope:

```json
{ "success": true, "message": "...", "data": {} }
{ "success": false, "message": "...", "error_code": "AUTH_FORBIDDEN" }
```

`data` holds the payload (object, array, or pagination object). Errors use proper HTTP status
codes (400, 401, 403, 404, 409, 422, 500). Stack traces are never returned to clients.

## Authentication (`/api/auth`)

| Method | Path          | Roles   | Purpose                    |
| ------ | ------------- | ------- | -------------------------- |
| POST   | /register     | Public  | Patient self-registration  |
| POST   | /login        | Public  | Login (email+password)     |
| POST   | /logout       | Any     | Revoke/clear token         |
| GET    | /me           | Any     | Current authenticated user |

Roles are issued at login; protected endpoints must be accessed with `Authorization: Bearer <token>`.

## Patient (`/api/patients`)

| Method | Path          | Roles   | Purpose                       |
| ------ | ------------- | ------- | ----------------------------- |
| GET    | /profile      | PATIENT | Own profile                   |
| PUT    | /profile      | PATIENT | Update own profile            |
| POST   | /problem      | PATIENT | Submit concern → AI suggestion|
| GET    | /history      | PATIENT | Own authorized history        |
| GET    | /appointments | PATIENT | Own appointments              |
| GET    | /recommendations | PATIENT | Own AI recommendations     |

## Departments (`/api/departments`)

| Method | Path       | Roles | Purpose                 |
| ------ | ---------- | ----- | ----------------------- |
| GET    | /          | Any   | List active departments |
| GET    | /:id       | Any   | Department detail       |
| GET    | /:id/doctors | Any | Doctors in department   |

## Doctors (`/api/doctors`)

| Method | Path                     | Roles | Purpose                    |
| ------ | ------------------------ | ----- | -------------------------- |
| GET    | /                        | Any   | Search/list doctors        |
| GET    | /:id                     | Any   | Doctor public profile      |
| GET    | /:id/availability        | Any   | Doctor availability slots  |

## Appointments (`/api/appointments`)

| Method | Path          | Roles          | Purpose                          |
| ------ | ------------- | -------------- | -------------------------------- |
| POST   | /             | PATIENT, ADMIN | Book appointment                 |
| GET    | /             | PATIENT, DOCTOR, ADMIN | List own/contextual |
| GET    | /:id          | Owner/Doctor/Admin | Detail                    |
| PUT    | /:id          | Doctor, Admin  | Confirm/cancel/complete          |
| DELETE | /:id          | Owner/Admin    | Cancel (owner)                   |

## Doctor (`/api/doctor`)

| Method | Path                | Roles   | Purpose                          |
| ------ | ------------------- | ------- | -------------------------------- |
| GET    | /dashboard          | DOCTOR  | Dashboard statistics             |
| GET    | /patients           | DOCTOR  | Authorized patients (list)       |
| GET    | /patients/:id       | DOCTOR  | Authorized case history          |
| POST   | /records            | DOCTOR  | Add clinical record              |
| POST   | /prescriptions      | DOCTOR  | Add prescription                 |
| POST   | /followups          | DOCTOR  | Add follow-up info               |
| GET    | /appointments       | DOCTOR  | Own appointments                 |
| PUT    | /appointments/:id   | DOCTOR  | Update appointment status        |
| GET/POST/PUT/DELETE | /availability | DOCTOR  | Manage availability slots     |

## Admin (`/api/admin`) — operational data only, no clinical detail

| Method | Path              | Roles  | Purpose                        |
| ------ | ----------------- | ------ | ------------------------------ |
| GET    | /dashboard        | ADMIN  | Operational statistics         |
| GET    | /users            | ADMIN  | Manage users                   |
| GET    | /patients         | ADMIN  | Operational patient list       |
| GET/POST/PUT | /doctors   | ADMIN  | Manage doctors                 |
| POST   | /assign-doctor    | ADMIN  | Assign doctor to patient/case  |
| GET/PUT | /appointments    | ADMIN  | Operational appointment mgmt   |
| GET/POST/PUT | /departments | ADMIN | Manage departments           |
| GET    | /reports          | ADMIN  | Operational reports            |

> Admin endpoints intentionally do **not** expose medical record contents, clinical
> assessments, prescriptions, or private notes.

## AI (`/api/ai`)

| Method | Path       | Roles   | Purpose                                  |
| ------ | ---------- | ------- | ---------------------------------------- |
| POST   | /recommend | PATIENT | Department suggestion (not a diagnosis)  |
| POST   | /chat      | PATIENT | Chat with AI assistant (demo/external)   |

## Response/Error Codes

Common `error_code` values: `VALIDATION_ERROR`, `AUTH_REQUIRED`, `AUTH_FORBIDDEN`,
`NOT_FOUND`, `CONFLICT` (e.g. double booking), `RATE_LIMITED`, `SERVER_ERROR`.

## Rate Limiting

Rate limiting is applied to auth and AI endpoints (configurable; enabled in production).
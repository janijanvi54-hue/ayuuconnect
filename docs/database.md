# AYUConnect – Database Design

MySQL (InnoDB, utf8mb4) via SQLAlchemy ORM in the application. SQLite is supported as a
local-development fallback (`sqlite:///ayuconnect_dev.db`) so the stack runs without a MySQL
server; the schema is identical in the ORM. `database/schema.sql` is the canonical DDL for
managed MySQL deployments.

## 1. Entities

```
users                    patient_cases            doctor_availability
patients                 medical_records         appointments
doctors                  prescriptions           followups
admins                   symptoms/categories     recommendations
departments              chat_sessions           notifications
                         chat_messages           audit_logs
```

## 2. ER Summary

```
users (role enum PATIENT|DOCTOR|ADMIN) 1───1 patients              (patient row per PATIENT user)
                                     1───1 doctors                (doctor row per DOCTOR user)
                                     1───1 admins                 (admin row per ADMIN user)

departments 1───────────────N doctors                              (doctor belongs to department)
departments 1───────────────N patients                             (suggested/assigned dept)

doctors 1─────N doctor_availability                                (weekly slot templates)
doctors 1─────N appointments
doctors 1─────N patient_cases                                      (authorized/assigned cases)
doctors 1─────N medical_records                                    (authored by doctor)

patients 1─────N appointments
patients 1─────N patient_cases
patients 1─────N recommendations                                  (AI dept suggestion history)
patients 1─────N chat_sessions 1─────N chat_messages
patients 1─────N notifications
patients 1─────N medical_records                                  (subject of record)

patient_cases 1─────N medical_records
patient_cases 1─────N prescriptions
patient_cases 1─────N followups

appointments N─────1 doctor_availability (optional: linked slot)
users N─────N audit_logs                                           (actor logs)
```

## 3. Key Tables

### users
| Column        | Type                      | Notes                          |
| ------------- | ------------------------- | ------------------------------ |
| id            | PK BIGINT UNSIGNED        |                                |
| email         | VARCHAR(190) UNIQUE, NN   | Unique constraint             |
| password_hash | VARCHAR(255) NN           | Werkzeug hash (never plain)   |
| full_name     | VARCHAR(120) NN           |                                |
| role          | ENUM(PATIENT,DOCTOR,ADMIN)|                                |
| phone         | VARCHAR(20)               |                                |
| is_active     | TINYINT(1) NN default 1   |                                |
| created_at    | DATETIME NN               |                                |
| updated_at    | DATETIME NN               |                                |

### patients, doctors, admins
One-to-one extension rows holding role-specific fields.
- `doctors`: department_id FK, license_no, specialization, bio, avatar, rating, is_available
- `patients`: date_of_birth, gender, blood_group, emergency_contact, consent flags

### departments
| Column   | Type            | Notes                        |
| -------- | --------------- | ---------------------------- |
| id       | PK              |                              |
| name     | VARCHAR(100) UQ | Ayurveda / Homeopathy / Unani / Yoga |
| slug     | VARCHAR(100) UQ |                              |
| description | TEXT        |                              |
| services | TEXT            | Services offered             |
| is_active| TINYINT(1) NN   | Admin can deactivate         |
| icon     | VARCHAR(50)     |                              |

### doctor_availability
Weekday-based slot templates.
| Column       | Type            | Notes                              |
| ------------ | --------------- | ---------------------------------- |
| id           | PK              |                                    |
| doctor_id    | FK doctors      |                                    |
| weekday      | TINYINT(0-6) NN | Monday=0 … Sunday=6                |
| start_time   | TIME NN         |                                    |
| end_time     | TIME NN         |                                    |
| is_active    | TINYINT(1) NN   | Mark unavailable without deleting  |
| UNIQUE(doctor_id, weekday, start_time, end_time) | prevents exact dupes |

Overlapping slots are rejected at the service layer.

### appointments
| Column         | Type       | Notes                              |
| -------------- | ---------- | ---------------------------------- |
| id             | PK         |                                    |
| patient_id     | FK patients|                                    |
| doctor_id      | FK doctors |                                    |
| department_id  | FK departments |                              |
| availability_id| FK doctor_availability | optional |       |
| date           | DATE NN    |                                    |
| start_time     | TIME NN    |                                    |
| end_time       | TIME NN    |                                    |
| status         | ENUM(PENDING, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW) |
| notes          | TEXT       |                                    |
| UNIQUE(doctor_id, date, start_time) | prevents double booking |

### patient_cases
Authorization hub between doctors and patient history.
| Column       | Type     | Notes                            |
| ------------ | -------- | -------------------------------- |
| id           | PK       |                                  |
| patient_id   | FK       |                                  |
| doctor_id    | FK       | assigning doctor                 |
| department_id| FK       |                                  |
| status       | ENUM(OPEN, ACTIVE, CLOSED) |                        |
| Uniques/case-insensitivity | (patient_id, doctor_id) |

> A doctor may only access a patient’s history through an authorized `patient_cases`
> row (or an appointment relationship). This is enforced in the doctor APIs.

### medical_records
| Column       | Type     | Notes                              |
| ------------ | -------- | ---------------------------------- |
| id           | PK       |                                    |
| case_id      | FK patient_cases |                          |
| patient_id   | FK patients |                                   |
| doctor_id    | FK doctors |                                    |
| record_type  | ENUM(INITIAL_ASSESSMENT, TREATMENT, FOLLOW_UP, NOTE, OTHER) |
| title        | VARCHAR(150) NN |                            |
| content      | TEXT NN  | Clinical content (doctor-only)     |
| is_visible_to_patient | TINYINT(1) NN default 1 |              |
| created_at / updated_at |           |                                    |

### prescriptions
| Column      | Type         | Notes                          |
| ----------- | ------------ | ------------------------------ |
| id          | PK           |                                |
| record_id   | FK medical_records |                       |
| case_id     | FK patient_cases    |                       |
| medicine/dosage/duration/instructions | VARCHAR/TEXT |  |
| created_at child rows in `prescription_items` if needed later |

### followups
| Column   | Type      | Notes                     |
| -------- | --------- | ------------------------- |
| id       | PK        |                           |
| case_id  | FK        |                           |
| scheduled_date | DATE |                            |
| instructions | TEXT  |                           |
| status   | ENUM(SCHEDULED, DONE, MISSED) |           |

### recommendations
| Column       | Type      | Notes                              |
| ------------ | --------- | ---------------------------------- |
| id           | PK        |                                    |
| patient_id   | FK        |                                    |
| category     | VARCHAR(60) | e.g. stress_wellness              |
| suggested_department_id | FK departments |                  |
| confidence   | FLOAT     |                                    |
| input_text   | TEXT      | Original concern text              |
| raw_response | JSON/TEXT | Rule-engine output                 |

### chat_sessions / chat_messages
Sessions per patient; messages with `sender` (USER|BOT), `content`, `provider`, timestamps.

### notifications
`user_id` FK, `type`, `title`, `body`, `is_read`, `link` (deep link). Channel abstraction
(in-app now; email/SMS later).

### audit_logs
| Column     | Type      | Notes                          |
| ---------- | --------- | ------------------------------ |
| id         | PK        |                                |
| user_id    | FK users (nullable for system) |              |
| action     | VARCHAR(60) | LOGIN, PATIENT_RECORD_VIEW, ... |
| resource   | VARCHAR(60) |                                |
| resource_id| VARCHAR(64) |                                |
| ip_address | VARCHAR(45) |                                |
| created_at | DATETIME  |                                |

Never store passwords, tokens, or secret payloads in audit logs.

## 4. Indexes
- `users(email)` unique
- `appointments(doctor_id, date)` , `appointments(patient_id)`
- `medical_records(patient_id)`, `medical_records(case_id)`
- `patient_cases(patient_id)`, `patient_cases(doctor_id)`
- `doctor_availability(doctor_id, weekday)`
- `audit_logs(user_id, created_at)`
- `notifications(user_id, is_read)`

## 5. Constraints & Integrity
- All FKs use `ON DELETE CASCADE`/`RESTRICT` deliberately per table (RESTRICT for doctors
  referenced by appointments; CASCADE for children of cases).
- NOT NULL plus default timestamps on created_at/updated_at.
- Unique composite key blocks exact duplicate availability and appointment double-booking.
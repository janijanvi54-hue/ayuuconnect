-- =====================================================================
-- AYUConnect - Canonical MySQL schema (utf8mb4, InnoDB)
-- Managed MySQL deployment DDL. The Flask/SQLAlchemy models mirror this.
-- =====================================================================

DROP DATABASE IF EXISTS ayuconnect;
CREATE DATABASE ayuconnect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ayuconnect;

-- ---------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(190) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(120) NOT NULL,
    role          ENUM('PATIENT','DOCTOR','ADMIN') NOT NULL,
    phone         VARCHAR(20) NULL,
    avatar_url    VARCHAR(255) NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_created (created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- departments
-- ---------------------------------------------------------------------
CREATE TABLE departments (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    services    TEXT NULL,
    icon        VARCHAR(50) NULL,
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- patients
-- ---------------------------------------------------------------------
CREATE TABLE patients (
    id                     BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id                BIGINT UNSIGNED NOT NULL UNIQUE,
    department_id          BIGINT UNSIGNED NULL,
    date_of_birth          DATE NULL,
    gender                 ENUM('MALE','FEMALE','OTHER') NULL,
    blood_group            VARCHAR(8) NULL,
    emergency_contact      VARCHAR(20) NULL,
    address                TEXT NULL,
    consent_records        TINYINT(1) NOT NULL DEFAULT 1,
    consent_ai             TINYINT(1) NOT NULL DEFAULT 1,
    created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_patients_user        FOREIGN KEY (user_id)       REFERENCES users(id)       ON DELETE CASCADE,
    CONSTRAINT fk_patients_department  FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    INDEX idx_patients_department (department_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- doctors
-- ---------------------------------------------------------------------
CREATE TABLE doctors (
    id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id        BIGINT UNSIGNED NOT NULL UNIQUE,
    department_id  BIGINT UNSIGNED NOT NULL,
    license_no     VARCHAR(60) NULL UNIQUE,
    specialization VARCHAR(120) NULL,
    bio            TEXT NULL,
    experience_years INT UNSIGNED NULL DEFAULT 0,
    rating         DECIMAL(3,2) NULL DEFAULT 0.00,
    is_available   TINYINT(1) NOT NULL DEFAULT 1,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_doctors_user        FOREIGN KEY (user_id)       REFERENCES users(id)       ON DELETE CASCADE,
    CONSTRAINT fk_doctors_department  FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
    INDEX idx_doctors_department (department_id),
    INDEX idx_doctors_available (is_available)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- admins
-- ---------------------------------------------------------------------
CREATE TABLE admins (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT UNSIGNED NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_admins_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- doctor_availability (weekly slot templates)
-- ---------------------------------------------------------------------
CREATE TABLE doctor_availability (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    doctor_id  BIGINT UNSIGNED NOT NULL,
    weekday    TINYINT NOT NULL COMMENT '0=Monday..6=Sunday',
    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,
    is_active  TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_availability (doctor_id, weekday, start_time, end_time),
    CONSTRAINT fk_avail_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    INDEX idx_avail_weekday (doctor_id, weekday)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- patient_cases (authorization hub between doctor <-> patient)
-- ---------------------------------------------------------------------
CREATE TABLE patient_cases (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id    BIGINT UNSIGNED NOT NULL,
    doctor_id     BIGINT UNSIGNED NOT NULL,
    department_id BIGINT UNSIGNED NULL,
    status        ENUM('OPEN','ACTIVE','CLOSED') NOT NULL DEFAULT 'OPEN',
    assigned_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_case_patient_doctor (patient_id, doctor_id),
    CONSTRAINT fk_cases_patient     FOREIGN KEY (patient_id)     REFERENCES patients(id)    ON DELETE CASCADE,
    CONSTRAINT fk_cases_doctor      FOREIGN KEY (doctor_id)      REFERENCES doctors(id)     ON DELETE RESTRICT,
    CONSTRAINT fk_cases_department  FOREIGN KEY (department_id)  REFERENCES departments(id) ON DELETE SET NULL,
    INDEX idx_cases_doctor (doctor_id),
    INDEX idx_cases_patient (patient_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- appointments
-- ---------------------------------------------------------------------
CREATE TABLE appointments (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id      BIGINT UNSIGNED NOT NULL,
    doctor_id       BIGINT UNSIGNED NOT NULL,
    department_id   BIGINT UNSIGNED NULL,
    availability_id BIGINT UNSIGNED NULL,
    date            DATE NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    status          ENUM('PENDING','CONFIRMED','COMPLETED','CANCELLED','NO_SHOW') NOT NULL DEFAULT 'PENDING',
    notes           TEXT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_appointment_doctor_slot (doctor_id, date, start_time),
    CONSTRAINT fk_appts_patient     FOREIGN KEY (patient_id)     REFERENCES patients(id)     ON DELETE CASCADE,
    CONSTRAINT fk_appts_doctor      FOREIGN KEY (doctor_id)      REFERENCES doctors(id)      ON DELETE RESTRICT,
    CONSTRAINT fk_appts_department  FOREIGN KEY (department_id)  REFERENCES departments(id)  ON DELETE SET NULL,
    CONSTRAINT fk_appts_availability FOREIGN KEY (availability_id) REFERENCES doctor_availability(id) ON DELETE SET NULL,
    INDEX idx_appts_patient (patient_id, date),
    INDEX idx_appts_doctor (doctor_id, date),
    INDEX idx_appts_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- medical_records (clinical content - DOCTOR ONLY)
-- ---------------------------------------------------------------------
CREATE TABLE medical_records (
    id                   BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id              BIGINT UNSIGNED NOT NULL,
    patient_id           BIGINT UNSIGNED NOT NULL,
    doctor_id            BIGINT UNSIGNED NOT NULL,
    record_type          ENUM('INITIAL_ASSESSMENT','TREATMENT','FOLLOW_UP','NOTE','OTHER') NOT NULL DEFAULT 'NOTE',
    title                VARCHAR(150) NOT NULL,
    content              TEXT NOT NULL,
    is_visible_to_patient TINYINT(1) NOT NULL DEFAULT 1,
    created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_records_case    FOREIGN KEY (case_id)    REFERENCES patient_cases(id)  ON DELETE CASCADE,
    CONSTRAINT fk_records_patient FOREIGN KEY (patient_id) REFERENCES patients(id)       ON DELETE CASCADE,
    CONSTRAINT fk_records_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctors(id)        ON DELETE RESTRICT,
    INDEX idx_records_patient (patient_id),
    INDEX idx_records_case (case_id),
    INDEX idx_records_doctor (doctor_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- prescriptions (clinical content - DOCTOR ONLY)
-- ---------------------------------------------------------------------
CREATE TABLE prescriptions (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    record_id    BIGINT UNSIGNED NULL,
    case_id      BIGINT UNSIGNED NOT NULL,
    medicine     VARCHAR(150) NOT NULL,
    dosage       VARCHAR(120) NULL,
    frequency    VARCHAR(120) NULL,
    duration     VARCHAR(120) NULL,
    instructions TEXT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rx_record FOREIGN KEY (record_id) REFERENCES medical_records(id) ON DELETE SET NULL,
    CONSTRAINT fk_rx_case   FOREIGN KEY (case_id)   REFERENCES patient_cases(id)   ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- followups
-- ---------------------------------------------------------------------
CREATE TABLE followups (
    id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id        BIGINT UNSIGNED NOT NULL,
    scheduled_date DATE NOT NULL,
    instructions   TEXT NULL,
    status         ENUM('SCHEDULED','DONE','MISSED') NOT NULL DEFAULT 'SCHEDULED',
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_followups_case FOREIGN KEY (case_id) REFERENCES patient_cases(id) ON DELETE CASCADE,
    INDEX idx_followups_date (case_id, scheduled_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- recommendations (AI suggestion history)
-- ---------------------------------------------------------------------
CREATE TABLE recommendations (
    id                       BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id               BIGINT UNSIGNED NOT NULL,
    department_id            BIGINT UNSIGNED NULL,
    category                 VARCHAR(60) NULL,
    confidence               FLOAT NULL,
    input_text               TEXT NOT NULL,
    raw_response             JSON NULL,
    created_at               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reco_patient   FOREIGN KEY (patient_id)     REFERENCES patients(id)     ON DELETE CASCADE,
    CONSTRAINT fk_reco_department FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    INDEX idx_reco_patient (patient_id, created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- chat_sessions / chat_messages
-- ---------------------------------------------------------------------
CREATE TABLE chat_sessions (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT UNSIGNED NOT NULL,
    title      VARCHAR(150) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE chat_messages (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id BIGINT UNSIGNED NOT NULL,
    sender     ENUM('USER','BOT') NOT NULL,
    content    TEXT NOT NULL,
    provider   VARCHAR(30) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_msg_session FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    INDEX idx_msg_session (session_id, created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- notifications
-- ---------------------------------------------------------------------
CREATE TABLE notifications (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT UNSIGNED NOT NULL,
    type       VARCHAR(40) NOT NULL,
    title      VARCHAR(150) NOT NULL,
    body       TEXT NULL,
    link       VARCHAR(255) NULL,
    is_read    TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user (user_id, is_read, created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- audit_logs
-- ---------------------------------------------------------------------
CREATE TABLE audit_logs (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT UNSIGNED NULL,
    action      VARCHAR(60) NOT NULL,
    resource    VARCHAR(60) NULL,
    resource_id VARCHAR(64) NULL,
    ip_address  VARCHAR(45) NULL,
    details     JSON NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_user (user_id, created_at),
    INDEX idx_audit_action (action, created_at)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- problem_categories (configurable rule mappings for the AI engine)
-- ---------------------------------------------------------------------
CREATE TABLE problem_categories (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    key           VARCHAR(60) NOT NULL UNIQUE,
    label         VARCHAR(120) NOT NULL,
    keywords      TEXT NULL,
    default_department_id BIGINT UNSIGNED NULL,
    min_confidence FLOAT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cat_department FOREIGN KEY (default_department_id) REFERENCES departments(id) ON DELETE SET NULL
) ENGINE=InnoDB;
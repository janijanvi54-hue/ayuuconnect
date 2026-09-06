-- =====================================================================
-- AYUConnect - Seed data (development only)
--
-- NOTE: demo users (patient@example.test, doctor@example.test,
-- admin@example.test) are created by the application seed command
-- (`flask seed-demo` / `python run.py --seed`) because password hashes
-- must be generated with Werkzeug. Their public profile data is seeded
-- here so it also works when the backend ORM seeds the DB.
--
-- All data below is clearly fictitious. Never use real patient data.
-- =====================================================================

USE ayuconnect;

-- ---------------------------------------------------------------------
-- Departments (the four core AYUSH departments)
-- ---------------------------------------------------------------------
INSERT INTO departments (name, slug, description, services, icon)
VALUES
('Ayurveda', 'ayurveda',
 'The ancient Indian system of medicine focusing on balance of body, mind, and doshas through diet, lifestyle, herbs, and therapies.',
 'Consultation, Panchakarma therapies, Herbal remedies, Diet & lifestyle guidance, Seasonal regimens',
 'leaf'),
('Homeopathy', 'homeopathy',
 'A system of medicine using highly diluted natural substances to stimulate the body''s own healing response.',
 'Consultation, Constitutional treatment, Acute care, Follow-up care',
 'droplet'),
('Unani', 'unani',
 'A traditional system influenced by Greek-Arabic medicine emphasizing the four humors and holistic healing.',
 'Consultation, Regimental therapy, Dietotherapy, Pharmacotherapy',
 'sun'),
('Yoga', 'yoga',
 'A mind-body practice integrating postures, breathwork, and meditation for wellness and stress management.',
 'Yoga therapy, Pranayama, Meditation, Stress management programs, Class plans',
 'lotus')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- ---------------------------------------------------------------------
-- Problem categories used by the recommendation engine
-- ---------------------------------------------------------------------
INSERT INTO problem_categories (label, `key`, keywords, default_department_id, min_confidence)
VALUES
('Stress & Wellness', 'stress_wellness',
 'stress, anxiety, sleep, insomnia, relaxation, tired, fatigue, tension, worried, overwhelmed, burnout, meditation, mindfulness', 4, 0.55),
('Digestive & Lifestyle', 'digestive_lifestyle',
 'digest, stomach, acidity, gas, bloating, indigestion, constipation, appetite, lifestyle, diet, weight', 1, 0.55),
('Chronic & Constitutional', 'chronic_constitutional',
 'allergy, skin, asthma, headache, joint, pain, immunity, chronic, sinus, migraine', 2, 0.50),
('Women''s Health', 'womens_health',
 'period, menstrual, pms, menopause, pregnancy, female, gynaec', 1, 0.50),
('General Wellness', 'general_wellness',
 'wellness, healthy, fitness, posture, back, neck, breathing, energy, focus, balance, preventive', 4, 0.45);

-- ---------------------------------------------------------------------
-- Demo public profile data (matched by the app seed command)
-- ---------------------------------------------------------------------

-- Demo doctors (user rows are created by the app seed command; these
-- rows use the user_id that the command creates for doctor@example.test).
-- The seed command inserts doctor/patient/admin extras programmatically
-- so it stays consistent with hashed credentials. The statements below
-- are illustrative and idempotent when run by the ORM seed assistant.
-- ---------------------------------------------------------------------

-- Note: To keep a single source of truth, the ORM seed command
-- (`backend/app/cli.py`) is the authoritative seeder for users,
-- doctors, patients, admins, availability, cases, appointments,
-- records, and notifications. Departments/categories above are the
-- canonical reference data committed in SQL.
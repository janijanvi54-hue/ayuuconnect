import { Link } from "react-router-dom";
import PublicLayout from "../../layouts/PublicLayout.jsx";

const DEPARTMENTS = [
  {
    name: "Ayurveda",
    icon: "🌿",
    text: "Balancing body, mind, and doshas through diet, lifestyle, herbs, and Panchakarma therapies.",
  },
  {
    name: "Homeopathy",
    icon: "💧",
    text: "Highly diluted natural substances that stimulate the body's own healing response.",
  },
  {
    name: "Unani",
    icon: "☀️",
    text: "A Greek–Arabic influenced system of humoral medicine with holistic healing traditions.",
  },
  {
    name: "Yoga",
    icon: "🪷",
    text: "Postures, breathwork, and meditation for wellness, flexibility, and stress management.",
  },
];

const STEPS = [
  {
    n: "1",
    title: "Describe your concern",
    text: "Tell us, in your own words, what you have been experiencing.",
  },
  {
    n: "2",
    title: "AI-assisted guidance",
    text: "Get a suggested AYUSH department — not a diagnosis — with a clear disclaimer.",
  },
  {
    n: "3",
    title: "Meet a practitioner",
    text: "Browse doctors, view live availability, and book an appointment.",
  },
  {
    n: "4",
    title: "Care continues",
    text: "Track appointments, follow-ups, and your authorized case history.",
  },
];

const FEATURES = [
  ["Personalized dashboard", "Everything you need in one calm, clear view."],
  ["Department recommendation", "Rule-based AI assistance to navigate AYUSH care."],
  ["Smart appointment booking", "Real availability, no double booking."],
  ["AI healthcare assistant", "Answers questions about navigating AYUConnect and AYUSH."],
  ["Authorized history", "You and your doctor see only what is authorized."],
  ["Role-based access", "Patients, doctors, and admins each have the right view."],
];

const AI_SAFETY_POINTS = [
  "The AI suggests departments and explains how the app works.",
  "It never claims to diagnose, prescribe, or replace a clinician.",
  "Urgent symptoms are directed to immediate professional/emergency care.",
  "Final clinical assessment is always made by a qualified practitioner.",
];

export default function Landing() {
  return (
    <PublicLayout>
      {/* Hero */}
      <section className="bg-white">
        <div className="container py-5">
          <div className="row align-items-center g-5">
            <div className="col-lg-6">
              <p className="badge badge-soft mb-3">AYUSH • AI-assisted • Integrated</p>
              <h1 className="display-5 fw-bold lh-sm section-title">
                Your path through AYUSH care, guided.
              </h1>
              <p className="lead text-muted mt-3">
                AYUConnect connects you with Ayurveda, Homeopathy, Unani, and Yoga
                practitioners — with an AI assistant that helps you find the right
                department, doctor, and appointment.
              </p>
              <div className="d-flex flex-wrap gap-2 mt-4">
                <Link to="/register" className="btn btn-primary btn-lg px-4">
                  Get Started
                </Link>
                <a
                  href="#departments"
                  className="btn btn-outline-primary btn-lg px-4"
                >
                  Explore Departments
                </a>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="p-4 rounded-4 bg-light border">
                <div className="d-flex align-items-center gap-3 mb-3">
                  <span className="badge-soft badge">AI Assistant</span>
                  <span className="text-muted small">Demo mode</span>
                </div>
                <div className="card mb-3">
                  <div className="card-body">
                    <p className="mb-1">
                      <strong>You:</strong> I have been feeling stressed and having
                      difficulty sleeping.
                    </p>
                    <p className="mb-0 mt-2">
                      <strong>Assistant:</strong> Based on the information provided,
                      you may consider consulting the <strong>Yoga</strong> department
                      for stress and relaxation support. This is an AI-assisted
                      suggestion, not a diagnosis.
                    </p>
                  </div>
                </div>
                <p className="small text-muted mb-0">
                  The assistant helps you navigate care. A qualified practitioner
                  always makes the final clinical assessment.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About */}
      <section id="about" className="py-5">
        <div className="container">
          <h2 className="section-title h3 mb-4">About AYUConnect</h2>
          <p className="text-muted col-lg-8 px-0">
            AYUConnect is a healthcare management and recommendation platform for the
            AYUSH systems of medicine. Patients, doctors, and administrators work from
            a single integrated system built around safety, privacy, and clear
            role-based access.
          </p>
        </div>
      </section>

      {/* Departments */}
      <section id="departments" className="py-5 bg-white">
        <div className="container">
          <h2 className="section-title h3 mb-4">AYUSH Departments</h2>
          <div className="row g-4">
            {DEPARTMENTS.map((d) => (
              <div className="col-md-6 col-lg-3" key={d.name}>
                <div className="card h-100">
                  <div className="card-body">
                    <div className="fs-2">{d.icon}</div>
                    <h5 className="mt-2">{d.name}</h5>
                    <p className="text-muted mb-0 small">{d.text}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-5">
        <div className="container">
          <h2 className="section-title h3 mb-4">How it works</h2>
          <div className="row g-4">
            {STEPS.map((s) => (
              <div className="col-md-6 col-lg-3" key={s.n}>
                <div className="d-flex gap-3">
                  <span className="badge rounded-circle bg-success text-white flex-shrink-0 d-inline-flex align-items-center justify-content-center"
                    style={{ width: "2.4rem", height: "2.4rem" }}>
                    {s.n}
                  </span>
                  <div>
                    <h6 className="mb-1">{s.title}</h6>
                    <p className="text-muted small mb-0">{s.text}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-5 bg-white">
        <div className="container">
          <h2 className="section-title h3 mb-4">Features</h2>
          <div className="row g-4">
            {FEATURES.map(([title, text]) => (
              <div className="col-md-6 col-lg-4" key={title}>
                <div className="d-flex gap-2">
                  <span className="text-success">✓</span>
                  <div>
                    <h6 className="mb-1">{title}</h6>
                    <p className="text-muted small mb-0">{text}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI assistant safety */}
      <section className="py-5">
        <div className="container">
          <div className="card">
            <div className="card-body p-4">
              <h2 className="section-title h4 mb-3">Our AI assistant is built safely</h2>
              <ul className="mb-0">
                {AI_SAFETY_POINTS.map((p) => (
                  <li key={p} className="text-muted mb-1">
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="pb-5">
        <div className="container">
          <div className="rounded-4 bg-success text-white p-4 p-md-5 text-center">
            <h2 className="section-title h3">Ready to begin your AYUSH journey?</h2>
            <p className="mb-4">
              Create your account, describe your concern, and get guided to the right care.
            </p>
            <Link to="/register" className="btn btn-light btn-lg px-4">
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="pb-5">
        <div className="container">
          <div className="disclaimer p-3 small">
            <strong>Important:</strong> AYUConnect provides general AYUSH information,
            department guidance, and appointment assistance. AI-assisted outputs are
            suggestions only and are not a medical diagnosis, prescription, or
            emergency medical advice. In an emergency, contact your local emergency
            services immediately.
          </div>
        </div>
      </section>
    </PublicLayout>
  );
}
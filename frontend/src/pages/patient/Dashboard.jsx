import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

function StatCard({ label, value }) {
  return (
    <div className="card h-100">
      <div className="card-body">
        <div className="small text-muted">{label}</div>
        <div className="h3 mb-0">{value}</div>
      </div>
    </div>
  );
}

StatCard.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
};

export default function PatientDashboard() {
  const [profile, setProfile] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [recommendations, setRecommendations] = useState(0);
  const [chatSessions, setChatSessions] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [p, a, r, c] = await Promise.all([
          api.get("/patients/profile"),
          api.get("/patients/appointments"),
          api.get("/patients/recommendations"),
          api.get("/patients/chat/sessions"),
        ]);
        setProfile(p.data.data.patient);
        setAppointments(a.data.data.appointments);
        setRecommendations(r.data.data.recommendations.length);
        setChatSessions(c.data.data.sessions.length);
      } catch (err) {
        setError(err.response?.data?.message || "Could not load your dashboard.");
      }
    })();
  }, []);

  const upcoming = appointments.filter(
    (a) => a.status === "PENDING" || a.status === "CONFIRMED"
  );

  return (
    <AppLayout>
      <div className="container">
        <h1 className="h3 mb-1">Hello, {profile?.full_name}</h1>
        <p className="text-muted small mb-4">
          {profile?.email} • {profile?.phone}
        </p>

        {error && <div className="alert alert-danger py-2">{error}</div>}

        <div className="row g-3 mb-4">
          <div className="col-6 col-lg-3">
            <StatCard label="Upcoming visits" value={upcoming.length} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Total appointments" value={appointments.length} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Health reports" value={recommendations} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Assistant chats" value={chatSessions} />
          </div>
        </div>

        <div className="d-flex flex-wrap gap-2 mb-4">
          <Link to="/patient/book" className="btn btn-primary">
            Book an appointment
          </Link>
          <Link to="/patient/recommendations" className="btn btn-outline-success">
            Check my health concern
          </Link>
          <Link to="/patient/chat" className="btn btn-outline-primary">
            Ask the assistant
          </Link>
        </div>

        <h2 className="h5 mb-3">Upcoming appointments</h2>
        {upcoming.length === 0 && (
          <div className="card">
            <div className="card-body text-muted">
              No upcoming visits.{" "}
              <Link to="/patient/book">Book your first appointment.</Link>
            </div>
          </div>
        )}
        <div className="list-group">
          {upcoming.map((a) => (
            <div className="list-group-item" key={a.id}>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="fw-semibold">{a.doctor_name}</div>
                  <div className="small text-muted">
                    {a.date} at {a.start_time} • {a.department?.name}
                  </div>
                </div>
                <span className={`badge text-bg-${a.status === "CONFIRMED" ? "success" : "warning"}`}>
                  {a.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
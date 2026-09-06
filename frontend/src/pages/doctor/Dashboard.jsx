import { useEffect, useState } from "react";
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

export default function DoctorDashboard() {
  const [stats, setStats] = useState({});
  const [today, setToday] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [s, a] = await Promise.all([
          api.get("/doctor/dashboard"),
          api.get("/doctor/appointments", { params: { status: "CONFIRMED" } }),
        ]);
        setStats(s.data.data.stats);
        const todaysDate = new Date().toISOString().slice(0, 10);
        setToday((a.data.data.appointments || []).filter((x) => x.date === todaysDate));
      } catch (err) {
        setError(err.response?.data?.message || "Could not load dashboard.");
      }
    })();
  }, []);

  return (
    <AppLayout>
      <div className="container">
        <h1 className="h3 mb-4">Doctor dashboard</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}

        <div className="row g-3 mb-4">
          <div className="col-6 col-lg-3">
            <StatCard label="Total patients" value={stats.total_patients ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Active cases" value={stats.active_cases ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Upcoming visits" value={stats.upcoming_appointments ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Pending requests" value={stats.pending_appointments ?? "—"} />
          </div>
        </div>

        <h2 className="h5 mb-3">Confirmed appointments today</h2>
        {today.length === 0 && (
          <div className="card">
            <div className="card-body text-muted">No confirmed appointments today.</div>
          </div>
        )}
        <div className="list-group">
          {today.map((a) => (
            <div className="list-group-item" key={a.id}>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="fw-semibold">{a.patient_name}</div>
                  <div className="small text-muted">{a.date} at {a.start_time}</div>
                </div>
                <span className="badge text-bg-success">{a.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
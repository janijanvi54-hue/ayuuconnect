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

export default function AdminDashboard() {
  const [stats, setStats] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/admin/dashboard")
      .then(({ data }) => setStats(data.data.stats))
      .catch((err) => setError(err.response?.data?.message || "Could not load stats."));
  }, []);

  return (
    <AppLayout>
      <div className="container">
        <h1 className="h3 mb-4">Admin dashboard</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        <div className="row g-3">
          <div className="col-6 col-lg-3">
            <StatCard label="Total users" value={stats.total_users ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Patients" value={stats.patients ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Doctors" value={stats.doctors ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Active departments" value={stats.active_departments ?? "—"} />
          </div>
        </div>
        <div className="row g-3 mt-1">
          <div className="col-6 col-lg-3">
            <StatCard label="Recommendations" value={stats.recommendations ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Appointments today" value={stats.appointments_today ?? "—"} />
          </div>
          <div className="col-6 col-lg-3">
            <StatCard label="Upcoming appointments" value={stats.upcoming_appointments ?? "—"} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
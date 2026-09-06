import { useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

const BADGE = {
  PENDING: "text-bg-warning",
  CONFIRMED: "text-bg-success",
  COMPLETED: "text-bg-secondary",
  CANCELLED: "text-bg-danger",
  NO_SHOW: "text-bg-dark",
};

export default function DoctorAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = async (status) => {
    try {
      const { data } = await api.get("/doctor/appointments", {
        params: status ? { status } : {},
      });
      setAppointments(data.data.appointments);
    } catch (err) {
      setError(err.response?.data?.message || "Could not load appointments.");
    }
  };

  useEffect(() => {
    load(filter);
  }, [filter]);

  const update = async (id, status) => {
    setBusyId(id);
    try {
      await api.patch(`/doctor/appointments/${id}`, { status });
      load(filter);
    } catch (err) {
      setError(err.response?.data?.message || "Update failed.");
    } finally {
      setBusyId(null);
    }
  };

  const next = (a) => {
    if (a.status === "PENDING") return ["CONFIRMED", "CANCELLED"];
    if (a.status === "CONFIRMED") return ["COMPLETED", "NO_SHOW"];
    return [];
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "56rem" }}>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Appointments</h1>
          <select className="form-select w-auto" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="">All statuses</option>
            {Object.keys(BADGE).map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {error && <div className="alert alert-danger py-2">{error}</div>}

        {appointments.length === 0 && (
          <div className="card">
            <div className="card-body text-muted">No appointments{filter ? ` with status ${filter}` : ""}.</div>
          </div>
        )}

        <div className="list-group">
          {appointments.map((a) => (
            <div className="list-group-item" key={a.id}>
              <div className="d-flex justify-content-between align-items-center gap-3">
                <div>
                  <div className="fw-semibold">{a.patient_name}</div>
                  <div className="small text-muted">
                    {a.date} at {a.start_time}–{a.end_time}
                  </div>
                  {a.notes && <div className="small text-muted mt-1">{a.notes}</div>}
                </div>
                <div className="d-flex align-items-center gap-2">
                  <span className={`badge ${BADGE[a.status] || "text-bg-secondary"}`}>{a.status}</span>
                  {next(a).map((s) => (
                    <button
                      key={s}
                      className={`btn btn-sm btn-outline-${s === "CONFIRMED" || s === "COMPLETED" ? "success" : s === "NO_SHOW" ? "dark" : "danger"}`}
                      disabled={busyId === a.id}
                      onClick={() => update(a.id, s)}
                    >
                      Mark {s.toLowerCase()}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
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

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const { data } = await api.get("/patients/appointments");
      setAppointments(data.data.appointments);
    } catch (err) {
      setError(err.response?.data?.message || "Could not load appointments.");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const cancel = async (id) => {
    try {
      await api.patch(`/patients/appointments/${id}/cancel`);
      load();
    } catch (err) {
      setError(err.response?.data?.message || "Could not cancel.");
    }
  };

  const cancellable = (a) => a.status === "PENDING" || a.status === "CONFIRMED";

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "52rem" }}>
        <h1 className="h3 mb-4">My appointments</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        {appointments.length === 0 && (
          <div className="card">
            <div className="card-body text-muted">No appointments yet.</div>
          </div>
        )}
        <div className="list-group">
          {appointments.map((a) => (
            <div className="list-group-item" key={a.id}>
              <div className="d-flex justify-content-between align-items-center gap-3">
                <div>
                  <div className="fw-semibold">{a.doctor_name}</div>
                  <div className="small text-muted">
                    {a.date} at {a.start_time}–{a.end_time} • {a.department?.name}
                  </div>
                  {a.notes && <div className="small text-muted mt-1">{a.notes}</div>}
                </div>
                <div className="d-flex align-items-center gap-2">
                  <span className={`badge ${BADGE[a.status] || "text-bg-secondary"}`}>{a.status}</span>
                  {cancellable(a) && (
                    <button className="btn btn-outline-danger btn-sm" onClick={() => cancel(a.id)}>
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
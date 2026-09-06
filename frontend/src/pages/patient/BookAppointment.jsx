import { useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export default function BookAppointment() {
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState([]);
  const [sel, setSel] = useState({ departmentSlug: "", doctorId: "", date: "", start: "" });
  const [message, setMessage] = useState({ kind: "", text: "" });
  const [loading, setLoading] = useState(false);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    api.get("/departments").then(({ data }) => setDepartments(data.data.departments)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!sel.departmentSlug) return;
    setDoctors([]);
    setSlots([]);
    api
      .get("/doctors", { params: { department: sel.departmentSlug } })
      .then(({ data }) => setDoctors(data.data.doctors))
      .catch(() => {});
  }, [sel.departmentSlug]);

  useEffect(() => {
    if (!sel.doctorId || !sel.date) return;
    setLoadingSlots(true);
    setSlots([]);
    api
      .get(`/doctors/${sel.doctorId}/slots`, { params: { date: sel.date } })
      .then(({ data }) => setSlots(data.data.slots))
      .finally(() => setLoadingSlots(false));
  }, [sel.doctorId, sel.date]);

  const canSubmit = sel.doctorId && sel.date && sel.start && !loading;

  const submit = async () => {
    setLoading(true);
    setMessage({ kind: "", text: "" });
    try {
      await api.post("/patients/appointments", {
        doctor_id: Number(sel.doctorId),
        date: sel.date,
        start_time: sel.start,
      });
      setMessage({ kind: "success", text: "Appointment requested! The clinic will confirm shortly." });
      setSel({ ...sel, start: "" });
    } catch (err) {
      setMessage({ kind: "danger", text: err.response?.data?.message || "Booking failed." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "46rem" }}>
        <h1 className="h3 mb-4">Book an appointment</h1>

        {message.text && (
          <div className={`alert alert-${message.kind} py-2`} role="alert">
            {message.text}
          </div>
        )}

        <div className="card">
          <div className="card-body">
            <div className="mb-3">
              <label className="form-label small">Department</label>
              <select
                className="form-select"
                value={sel.departmentSlug}
                onChange={(e) => setSel({ ...sel, departmentSlug: e.target.value, doctorId: "", date: "", start: "" })}
              >
                <option value="">Select a department…</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.slug}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-3">
              <label className="form-label small">Doctor</label>
              <select
                className="form-select"
                value={sel.doctorId}
                onChange={(e) => setSel({ ...sel, doctorId: e.target.value, date: "", start: "" })}
                disabled={!sel.departmentSlug}
              >
                <option value="">Select a doctor…</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.full_name} • {d.specialization}
                  </option>
                ))}
              </select>
            </div>

            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label small">Date</label>
                <input
                  type="date"
                  className="form-control"
                  min={todayISO()}
                  value={sel.date}
                  onChange={(e) => setSel({ ...sel, date: e.target.value, start: "" })}
                  disabled={!sel.doctorId}
                />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label small">Free slots</label>
                <div>
                  {loadingSlots && <span className="text-muted small">Loading slots…</span>}
                  {!loadingSlots && slots.length === 0 && sel.date && (
                    <span className="text-muted small">No free slots on this date.</span>
                  )}
                  {slots.map((s) => (
                    <button
                      key={s.start_time}
                      type="button"
                      className={`btn btn-sm m-1 ${
                        sel.start === s.start_time ? "btn-success" : "btn-outline-success"
                      }`}
                      onClick={() => setSel({ ...sel, start: s.start_time })}
                    >
                      {s.start_time}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button className="btn btn-primary w-100" disabled={!canSubmit} onClick={submit}>
              {loading ? "Requesting…" : "Request appointment"}
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
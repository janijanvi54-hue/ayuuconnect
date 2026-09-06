import { useCallback, useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function Availability() {
  const [slots, setSlots] = useState([]);
  const [form, setForm] = useState({ weekday: "1", start_time: "10:00", end_time: "11:00" });
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    const { data } = await api.get("/doctor/availability");
    setSlots(data.data.availability);
  }, []);

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || "Could not load slots."));
  }, [load]);

  const add = async () => {
    setError("");
    try {
      await api.post("/doctor/availability", form);
      load();
    } catch (err) {
      setError(err.response?.data?.message || "Could not add slot.");
    }
  };

  const remove = useCallback(
    async (id) => {
      setBusyId(id);
      try {
        await api.delete(`/doctor/availability/${id}`);
        load();
      } catch (err) {
        setError(err.response?.data?.message || "Could not delete slot.");
      } finally {
        setBusyId(null);
      }
    },
    [load]
  );

  const groups = slots.reduce((acc, s) => {
    (acc[s.weekday] = acc[s.weekday] || []).push(s);
    return acc;
  }, {});

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "46rem" }}>
        <h1 className="h3 mb-4">My availability</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}

        <div className="card mb-4">
          <div className="card-body">
            <div className="row g-3 align-items-end">
              <div className="col-md-3">
                <label className="form-label small">Day</label>
                <select
                  className="form-select"
                  value={form.weekday}
                  onChange={(e) => setForm({ ...form, weekday: e.target.value })}
                >
                  {WEEKDAYS.map((d, i) => (
                    <option key={i} value={String(i)}>{d}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-3">
                <label className="form-label small">Start</label>
                <input
                  type="time"
                  className="form-control"
                  value={form.start_time}
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                />
              </div>
              <div className="col-md-3">
                <label className="form-label small">End</label>
                <input
                  type="time"
                  className="form-control"
                  value={form.end_time}
                  onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                />
              </div>
              <div className="col-md-3">
                <button className="btn btn-primary w-100" onClick={add}>
                  Add slot
                </button>
              </div>
            </div>
          </div>
        </div>

        {Object.entries(groups)
          .sort(([a], [b]) => a - b)
          .map(([weekday, list]) => (
            <div className="card mb-3" key={weekday}>
              <div className="card-body d-flex justify-content-between align-items-center">
                <div>
                  <div className="fw-semibold">{WEEKDAYS[Number(weekday)]}</div>
                  {list.map((s) => (
                    <div key={s.id} className="small text-muted">
                      {s.start_time}–{s.end_time} {s.is_active ? "" : "(deactivated)"}
                    </div>
                  ))}
                </div>
                <button
                  className="btn btn-outline-danger btn-sm"
                  disabled={busyId !== null}
                  onClick={() => list.forEach((s) => remove(s.id))}
                >
                  Deactivate
                </button>
              </div>
            </div>
          ))}

        {Object.keys(groups).length === 0 && (
          <div className="card">
            <div className="card-body text-muted">
              No availability set yet. Patients can only book on days you have a slot.
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
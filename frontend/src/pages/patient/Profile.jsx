import { useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Profile() {
  const [form, setForm] = useState({});
  const [saved, setSaved] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/patients/profile")
      .then(({ data }) => setForm(data.data.patient))
      .catch((err) => setError(err.response?.data?.message || "Could not load profile."));
  }, []);

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const save = async () => {
    setSaved("");
    setError("");
    try {
      const { data } = await api.put("/patients/profile", form);
      setForm(data.data.patient);
      setSaved("Profile updated.");
    } catch (err) {
      setError(err.response?.data?.message || "Could not save profile.");
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "46rem" }}>
        <h1 className="h3 mb-4">My profile</h1>
        {saved && <div className="alert alert-success py-2">{saved}</div>}
        {error && <div className="alert alert-danger py-2">{error}</div>}

        <div className="card">
          <div className="card-body">
            <div className="row g-3">
              <div className="col-md-6">
                <label className="form-label small">Full name</label>
                <input className="form-control" value={form.full_name || ""} onChange={(e) => set("full_name", e.target.value)} />
              </div>
              <div className="col-md-6">
                <label className="form-label small">Email (read only)</label>
                <input className="form-control" value={form.email || ""} disabled />
              </div>
              <div className="col-md-6">
                <label className="form-label small">Phone</label>
                <input className="form-control" value={form.phone || ""} onChange={(e) => set("phone", e.target.value)} />
              </div>
              <div className="col-md-6">
                <label className="form-label small">Gender</label>
                <select className="form-select" value={form.gender || ""} onChange={(e) => set("gender", e.target.value)}>
                  <option value="">Select…</option>
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
              <div className="col-md-6">
                <label className="form-label small">Date of birth</label>
                <input
                  type="date"
                  className="form-control"
                  value={form.date_of_birth || ""}
                  onChange={(e) => set("date_of_birth", e.target.value)}
                />
              </div>
              <div className="col-md-6">
                <label className="form-label small">Blood group</label>
                <select className="form-select" value={form.blood_group || ""} onChange={(e) => set("blood_group", e.target.value)}>
                  <option value="">Unknown</option>
                  {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-6">
                <label className="form-label small">Emergency contact</label>
                <input className="form-control" value={form.emergency_contact || ""} onChange={(e) => set("emergency_contact", e.target.value)} />
              </div>
              <div className="col-md-6">
                <label className="form-label small">Preferred department</label>
                <input className="form-control" value={form.department_id || ""} onChange={(e) => set("department_id", e.target.value)} />
              </div>
              <div className="col-12">
                <label className="form-label small">Address</label>
                <textarea className="form-control" rows={2} value={form.address || ""} onChange={(e) => set("address", e.target.value)} />
              </div>
              <div className="col-12">
                <div className="form-check form-switch">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={!!form.consent_ai}
                    onChange={(e) => set("consent_ai", e.target.checked)}
                  />
                  <label className="form-check-label small">
                    Allow AI-assisted recommendations (Check my health concern)
                  </label>
                </div>
              </div>
            </div>
            <button className="btn btn-primary mt-4" onClick={save}>
              Save changes
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
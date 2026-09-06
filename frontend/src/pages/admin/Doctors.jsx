import { useCallback, useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState({
    full_name: "", email: "", password: "", specialization: "", experience_years: "",
    department_id: "", phone: "", license_no: "",
  });
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(async () => {
    const [d, dep] = await Promise.all([
      api.get("/admin/doctors"),
      api.get("/departments"),
    ]);
    setDoctors(d.data.data.doctors);
    setDepartments(dep.data.data.departments);
  }, []);

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || "Could not load doctors."));
  }, [load]);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const create = async () => {
    setError("");
    try {
      await api.post("/admin/doctors", {
        ...form,
        department_id: Number(form.department_id),
        experience_years: Number(form.experience_years || 0),
      });
      setShowForm(false);
      setForm({});
      load();
    } catch (err) {
      setError(err.response?.data?.message || "Could not create doctor.");
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "60rem" }}>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Doctors</h1>
          <button className="btn btn-primary" onClick={() => setShowForm((s) => !s)}>
            {showForm ? "Close" : "Add doctor"}
          </button>
        </div>

        {error && <div className="alert alert-danger py-2">{error}</div>}

        {showForm && (
          <div className="card mb-4">
            <div className="card-body">
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label small">Full name</label>
                  <input className="form-control" value={form.full_name} onChange={(e) => set("full_name", e.target.value)} />
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Email</label>
                  <input className="form-control" value={form.email} onChange={(e) => set("email", e.target.value)} />
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Password (min 8 chars)</label>
                  <input type="password" className="form-control" value={form.password} onChange={(e) => set("password", e.target.value)} />
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Department</label>
                  <select className="form-select" value={form.department_id} onChange={(e) => set("department_id", e.target.value)}>
                    <option value="">Select…</option>
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Specialization</label>
                  <input className="form-control" value={form.specialization} onChange={(e) => set("specialization", e.target.value)} />
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Experience (years)</label>
                  <input type="number" className="form-control" value={form.experience_years} onChange={(e) => set("experience_years", e.target.value)} />
                </div>
                <div className="col-md-6">
                  <label className="form-label small">Phone</label>
                  <input className="form-control" value={form.phone} onChange={(e) => set("phone", e.target.value)} />
                </div>
                <div className="col-md-6">
                  <label className="form-label small">License number</label>
                  <input className="form-control" value={form.license_no} onChange={(e) => set("license_no", e.target.value)} />
                </div>
                <div className="col-12">
                  <button className="btn btn-primary" onClick={create}>Create doctor</button>
                  <button className="btn btn-outline-secondary ms-2" onClick={() => setShowForm(false)}>Cancel</button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Specialization</th>
                  <th>Experience</th>
                  <th>Email</th>
                </tr>
              </thead>
              <tbody>
                {doctors.map((d) => (
                  <tr key={d.id}>
                    <td className="fw-semibold">{d.full_name}</td>
                    <td>{d.department?.name || "—"}</td>
                    <td>{d.specialization || "—"}</td>
                    <td>{d.experience_years} yrs</td>
                    <td>{d.email}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
import { useCallback, useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Departments() {
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState({ name: "", slug: "", description: "" });
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(async () => {
    const { data } = await api.get("/admin/departments");
    setDepartments(data.data.departments);
  }, []);

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || "Could not load departments."));
  }, [load]);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const create = async () => {
    setError("");
    try {
      await api.post("/admin/departments", form);
      setShowForm(false);
      setForm({});
      load();
    } catch (err) {
      setError(err.response?.data?.message || "Could not create department.");
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "46rem" }}>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Departments</h1>
          <button className="btn btn-primary" onClick={() => setShowForm((s) => !s)}>
            {showForm ? "Close" : "Add department"}
          </button>
        </div>

        {error && <div className="alert alert-danger py-2">{error}</div>}

        {showForm && (
          <div className="card mb-4">
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label small">Name</label>
                <input className="form-control" value={form.name} onChange={(e) => set("name", e.target.value)} />
              </div>
              <div className="mb-3">
                <label className="form-label small">Slug</label>
                <input className="form-control" value={form.slug} onChange={(e) => set("slug", e.target.value)} />
              </div>
              <div className="mb-3">
                <label className="form-label small">Description</label>
                <textarea className="form-control" rows={3} value={form.description} onChange={(e) => set("description", e.target.value)} />
              </div>
              <button className="btn btn-primary" onClick={create}>Create</button>
              <button className="btn btn-outline-secondary ms-2" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </div>
        )}

        <div className="list-group">
          {departments.map((d) => (
            <div className="list-group-item" key={d.id}>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="fw-semibold">{d.name}</div>
                  <div className="small text-muted">{d.description}</div>
                </div>
                <span className={`badge ${d.is_active ? "text-bg-success" : "text-bg-secondary"}`}>
                  {d.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          ))}
        </div>

        {departments.length === 0 && (
          <div className="card">
            <div className="card-body text-muted">No departments yet.</div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
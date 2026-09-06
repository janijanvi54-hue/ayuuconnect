import { useCallback, useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Audit() {
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    const { data } = await api.get("/admin/audit-logs");
    setEntries(data.data.logs);
  }, []);

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || "Could not load audit log."));
  }, [load]);

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "60rem" }}>
        <h1 className="h3 mb-4">Audit log</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th>When</th>
                  <th>User</th>
                  <th>Role</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e) => (
                  <tr key={e.id}>
                    <td className="small">{new Date(e.created_at).toLocaleString()}</td>
                    <td>{e.user_name || e.user_email}</td>
                    <td><code>{e.action}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        {entries.length === 0 && (
          <div className="card">
            <div className="card-body text-muted">No audit entries yet.</div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
import { useCallback, useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

const ROLE_BADGE = { patient: "text-bg-primary", doctor: "text-bg-success", admin: "text-bg-danger" };

export default function Users() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    const { data } = await api.get("/admin/users");
    setUsers(data.data.users);
  }, []);

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || "Could not load users."));
  }, [load]);

  const toggle = async (u) => {
    setBusyId(u.id);
    try {
      await api.patch(`/admin/users/${u.id}`, { is_active: !u.is_active });
      load();
    } catch (err) {
      setError(err.response?.data?.message || "Update failed.");
    } finally {
      setBusyId(null);
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "60rem" }}>
        <h1 className="h3 mb-4">Users</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th className="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td className="fw-semibold">{u.full_name}</td>
                    <td>{u.email}</td>
                    <td>
                      <span className={`badge ${ROLE_BADGE[u.role] || "text-bg-secondary"}`}>{u.role}</span>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? "text-bg-success" : "text-bg-secondary"}`}>
                        {u.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td className="text-end">
                      {u.role !== "admin" && (
                        <button
                          className={`btn btn-sm ${u.is_active ? "btn-outline-danger" : "btn-outline-success"}`}
                          disabled={busyId === u.id}
                          onClick={() => toggle(u)}
                        >
                          {u.is_active ? "Disable" : "Enable"}
                        </button>
                      )}
                    </td>
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
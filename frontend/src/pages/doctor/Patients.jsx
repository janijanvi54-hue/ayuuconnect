import { useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [selected, setSelected] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    const { data } = await api.get("/doctor/patients");
    setPatients(data.data.patients);
  };

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || "Could not load patients."));
  }, []);

  const select = async (item) => {
    const patient = item.patient;
    setSelected(patient.id);
    setHistory([]);
    try {
      const { data } = await api.get(`/doctor/patients/${patient.id}/records`);
      setHistory(data.data.history);
    } catch (err) {
      setError(err.response?.data?.message || "Could not load records.");
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "60rem" }}>
        <h1 className="h3 mb-4">My patients</h1>
        {error && <div className="alert alert-danger py-2">{error}</div>}

        <div className="row g-3">
          <div className="col-md-5">
            <div className="card">
              <div className="card-body">
                <h2 className="h6 mb-3">Patients with visits</h2>
                {patients.length === 0 && <div className="text-muted small">No patients yet.</div>}
                <div className="list-group">
                  {patients.map((item) => (
                    <button
                      key={item.patient.id}
                      className={`list-group-item list-group-item-action ${selected === item.patient.id ? "active" : ""}`}
                      onClick={() => select(item)}
                    >
                      <div className="fw-semibold">{item.patient.full_name}</div>
                      <div className="small">
                        {item.patient.gender || "—"} • {item.patient.blood_group || "blood group n/a"}
                      </div>
                      <div className="small text-muted">
                        {item.case.status} • {item.case.records_count} record{item.case.records_count === 1 ? "" : "s"}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-7">
            <div className="card">
              <div className="card-body">
                <h2 className="h6 mb-3">Health records</h2>
                {!selected && <div className="text-muted small">Select a patient to see their records.</div>}
                {selected && history.length === 0 && (
                  <div className="text-muted small">No shared records for this patient.</div>
                )}
                {history.map((h, i) => (
                  <div className="border rounded-3 p-3 mb-3" key={`${h.case.id}-${i}`}>
                    <div className="fw-semibold">
                      Case #{h.case.id} • {h.case.department?.name || "General"}
                    </div>
                    <div className="small text-muted">{h.case.status}</div>
                    {h.records.map((r) => (
                      <div className="mt-2" key={r.id}>
                        <div className="small fw-semibold">{r.title}</div>
                        <div className="small text-muted">{new Date(r.created_at).toLocaleString()}</div>
                        {r.content && <div className="small ps-2">{r.content}</div>}
                        {r.prescriptions.length > 0 && (
                          <div className="small ps-2 text-muted">
                            Prescriptions:{" "}
                            {r.prescriptions.map((p) => (
                              <span key={p.id}>
                                {p.medicine} ({p.dosage}, {p.frequency}, {p.duration}){" "}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                    {h.followups.length > 0 && (
                      <div className="small ps-2 text-muted mt-2">
                        Follow-ups:{" "}
                        {h.followups.map((f) => (
                          <span key={f.id}>{f.scheduled_date} ({f.status}) </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
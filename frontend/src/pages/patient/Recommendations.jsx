import { useEffect, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Recommendations() {
  const [list, setList] = useState([]);
  const [concern, setConcern] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    const { data } = await api.get("/patients/recommendations");
    setList(data.data.recommendations);
  };

  useEffect(() => {
    load().catch(() => {});
  }, []);

  const submit = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await api.post("/patients/recommendations", { concern });
      setResult(data.data.recommendation);
      setConcern("");
      load();
    } catch (err) {
      setError(err.response?.data?.message || "Could not generate a recommendation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "46rem" }}>
        <h1 className="h3 mb-1">Check my health concern</h1>
        <p className="text-muted small mb-4">
          Describe your symptoms in your own words. We will suggest the most relevant
          AYUSH department. This is guidance only — never a diagnosis.
        </p>

        <div className="card mb-4">
          <div className="card-body">
            <textarea
              className="form-control mb-3"
              rows={4}
              placeholder="e.g. I have been feeling bloated after meals and low on energy…"
              value={concern}
              onChange={(e) => setConcern(e.target.value)}
            />
            <button className="btn btn-primary" onClick={submit} disabled={loading || concern.trim().length < 10}>
              {loading ? "Analyzing…" : "Get recommendation"}
            </button>
          </div>
        </div>

        {error && <div className="alert alert-danger py-2">{error}</div>}

        {result && (
          <div className="card border-success mb-4">
            <div className="card-body">
              <h2 className="h5 text-success mb-2">
                Suggested: {result.department?.name || "General health advice"}
              </h2>
              <p className="mb-2">{result.raw_response?.rationale}</p>
              <div className="small text-muted">
                Confidence {Math.round((result.confidence || 0) * 100)}% • Category: {result.category}
              </div>
            </div>
          </div>
        )}

        <h2 className="h5 mb-3">Previous recommendations</h2>
        {list.length === 0 && <div className="card"><div className="card-body text-muted">No recommendations yet.</div></div>}
        <div className="list-group">
          {list.map((r) => (
            <div className="list-group-item" key={r.id}>
              <div className="fw-semibold">{r.department?.name || "General advice"}</div>
              <div className="small text-muted">
                {new Date(r.created_at).toLocaleString()} • {r.category} •{" "}
                {Math.round((r.confidence || 0) * 100)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
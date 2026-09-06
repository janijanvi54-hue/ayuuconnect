import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../services/api.js";
import { useAuth } from "../../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState("");
  const [loading, setLoading] = useState(false);

  const redirectFor = (role) => {
    const map = {
      PATIENT: "/patient/dashboard",
      DOCTOR: "/doctor/dashboard",
      ADMIN: "/admin/dashboard",
    };
    return map[role] || "/";
  };

  const validate = () => {
    const next = {};
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!form.email.trim()) next.email = "Email is required.";
    else if (!emailRe.test(form.email.trim())) next.email = "Enter a valid email address.";
    if (!form.password) next.password = "Password is required.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitError("");
    if (!validate()) return;
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", {
        email: form.email.trim(),
        password: form.password,
      });
      if (data.success) {
        login(data.data.access_token, data.data.user);
        navigate(redirectFor(data.data.user.role), { replace: true });
      }
    } catch (err) {
      const msg = err.response?.data?.message || "Unable to log in. Please try again.";
      setSubmitError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100 p-3">
      <div className="card" style={{ width: "100%", maxWidth: "26rem" }}>
        <div className="card-body p-4">
          <Link to="/" className="fw-bold text-decoration-none">
            AYU<span className="text-success">Connect</span>
          </Link>
          <h1 className="h4 mt-3 mb-1 section-title">Welcome back</h1>
          <p className="text-muted small mb-4">
            Log in to your patient, doctor, or admin dashboard.
          </p>

          {submitError && <div className="alert alert-danger py-2 small">{submitError}</div>}

          <form onSubmit={onSubmit} noValidate>
            <div className="mb-3">
              <label htmlFor="email" className="form-label small">
                Email
              </label>
              <input
                id="email"
                type="email"
                className={`form-control ${errors.email ? "is-invalid" : ""}`}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.email && <div className="invalid-feedback">{errors.email}</div>}
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label small">
                Password
              </label>
              <input
                id="password"
                type="password"
                className={`form-control ${errors.password ? "is-invalid" : ""}`}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                autoComplete="current-password"
              />
              {errors.password && <div className="invalid-feedback">{errors.password}</div>}
            </div>

            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? "Logging in…" : "Log in"}
            </button>
          </form>

          <p className="text-center small text-muted mt-4 mb-0">
            New patient? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
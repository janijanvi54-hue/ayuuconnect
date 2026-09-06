import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../services/api.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+\d][\d\s-]{7,14}$/;

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState("");
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const next = {};
    if (!form.fullName.trim()) next.fullName = "Full name is required.";
    if (!form.email.trim()) next.email = "Email is required.";
    else if (!EMAIL_RE.test(form.email.trim())) next.email = "Enter a valid email address.";
    if (!form.phone.trim()) next.phone = "Phone number is required.";
    else if (!PHONE_RE.test(form.phone.trim())) next.phone = "Enter a valid phone number.";
    if (!form.password) next.password = "Password is required.";
    else if (form.password.length < 8) next.password = "Password must be at least 8 characters.";
    if (form.confirmPassword !== form.password) next.confirmPassword = "Passwords do not match.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitError("");
    if (!validate()) return;
    setLoading(true);
    try {
      const { data } = await api.post("/auth/register", {
        full_name: form.fullName.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        password: form.password,
      });
      if (data.success) {
        navigate("/login", { state: { registered: true } });
      }
    } catch (err) {
      const msg =
        err.response?.data?.message || "Unable to register. Please try again.";
      setSubmitError(msg);
    } finally {
      setLoading(false);
    }
  };

  const field = (key) => ({
    value: form[key],
    onChange: (e) => setForm({ ...form, [key]: e.target.value }),
  });

  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100 p-3">
      <div className="card" style={{ width: "100%", maxWidth: "26rem" }}>
        <div className="card-body p-4">
          <Link to="/" className="fw-bold text-decoration-none">
            AYU<span className="text-success">Connect</span>
          </Link>
          <h1 className="h4 mt-3 mb-1 section-title">Create your patient account</h1>
          <p className="text-muted small mb-4">
            Doctors create accounts through the administrator.
          </p>

          {submitError && <div className="alert alert-danger py-2 small">{submitError}</div>}

          <form onSubmit={onSubmit} noValidate>
            <div className="mb-3">
              <label htmlFor="fullName" className="form-label small">
                Full name
              </label>
              <input
                id="fullName"
                type="text"
                className={`form-control ${errors.fullName ? "is-invalid" : ""}`}
                {...field("fullName")}
                autoComplete="name"
              />
              {errors.fullName && <div className="invalid-feedback">{errors.fullName}</div>}
            </div>

            <div className="mb-3">
              <label htmlFor="email" className="form-label small">
                Email
              </label>
              <input
                id="email"
                type="email"
                className={`form-control ${errors.email ? "is-invalid" : ""}`}
                {...field("email")}
                autoComplete="email"
              />
              {errors.email && <div className="invalid-feedback">{errors.email}</div>}
            </div>

            <div className="mb-3">
              <label htmlFor="phone" className="form-label small">
                Phone
              </label>
              <input
                id="phone"
                type="tel"
                className={`form-control ${errors.phone ? "is-invalid" : ""}`}
                {...field("phone")}
                autoComplete="tel"
              />
              {errors.phone && <div className="invalid-feedback">{errors.phone}</div>}
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label small">
                Password
              </label>
              <input
                id="password"
                type="password"
                className={`form-control ${errors.password ? "is-invalid" : ""}`}
                {...field("password")}
                autoComplete="new-password"
              />
              {errors.password && <div className="invalid-feedback">{errors.password}</div>}
            </div>

            <div className="mb-4">
              <label htmlFor="confirmPassword" className="form-label small">
                Confirm password
              </label>
              <input
                id="confirmPassword"
                type="password"
                className={`form-control ${errors.confirmPassword ? "is-invalid" : ""}`}
                {...field("confirmPassword")}
                autoComplete="new-password"
              />
              {errors.confirmPassword && (
                <div className="invalid-feedback">{errors.confirmPassword}</div>
              )}
            </div>

            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="text-center small text-muted mt-4 mb-0">
            Already registered? <Link to="/login">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
import { Link, NavLink, useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import api from "../services/api.js";
import { useAuth } from "../context/AuthContext.jsx";
import NotificationDropdown from "../components/NotificationDropdown.jsx";

const NAV = {
  PATIENT: [
    ["Dashboard", "/patient/dashboard"],
    ["Book visit", "/patient/book"],
    ["Appointments", "/patient/appointments"],
    ["My Health", "/patient/recommendations"],
    ["Assistant", "/patient/chat"],
    ["Profile", "/patient/profile"],
  ],
  DOCTOR: [
    ["Dashboard", "/doctor/dashboard"],
    ["Appointments", "/doctor/appointments"],
    ["Availability", "/doctor/availability"],
    ["Patients", "/doctor/patients"],
  ],
  ADMIN: [
    ["Dashboard", "/admin/dashboard"],
    ["Users", "/admin/users"],
    ["Doctors", "/admin/doctors"],
    ["Departments", "/admin/departments"],
    ["Audit", "/admin/audit"],
  ],
};

export default function AppLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const items = NAV[user?.role] || [];

  const onLogout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      /* token is discarded regardless */
    }
    logout();
    navigate("/", { replace: true });
  };

  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      <nav className="navbar navbar-expand-lg bg-white border-bottom sticky-top">
        <div className="container">
          <Link to={items[0]?.[1] || "/"} className="navbar-brand fw-bold">
            AYU<span className="text-success">Connect</span>
          </Link>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#appNav"
            aria-controls="appNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon" />
          </button>
          <div className="collapse navbar-collapse" id="appNav">
            <ul className="navbar-nav mx-auto">
              {items.map(([label, to]) => (
                <li className="nav-item" key={to}>
                  <NavLink
                    to={to}
                    end={to === items[0]?.[1]}
                    className={({ isActive }) =>
                      `nav-link ${isActive ? "active fw-semibold" : ""}`
                    }
                  >
                    {label}
                  </NavLink>
                </li>
              ))}
            </ul>
            <div className="d-flex align-items-center gap-3">
              <NotificationDropdown />
              <span className="small text-muted d-none d-md-inline">{user?.full_name}</span>
              <button className="btn btn-outline-danger btn-sm" onClick={onLogout}>
                Log out
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-grow-1 py-4">{children}</main>
    </div>
  );
}

AppLayout.propTypes = {
  children: PropTypes.node.isRequired,
};
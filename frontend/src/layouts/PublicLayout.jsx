import { Link, NavLink } from "react-router-dom";
import PropTypes from "prop-types";

// Public site chrome: responsive navbar + footer used by the landing page.
export default function PublicLayout({ children }) {
  return (
    <div className="d-flex flex-column min-vh-100">
      <nav className="navbar navbar-expand-lg bg-white border-bottom sticky-top">
        <div className="container">
          <Link to="/" className="navbar-brand fw-bold">
            AYU<span className="text-success">Connect</span>
          </Link>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#publicNav"
            aria-controls="publicNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon" />
          </button>
          <div className="collapse navbar-collapse" id="publicNav">
            <ul className="navbar-nav ms-auto align-items-lg-center gap-lg-2">
              <li className="nav-item">
                <NavLink
                  to="/#about"
                  className="nav-link"
                  onClick={() => document.getElementById("about")?.scrollIntoView()}
                >
                  About
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/#departments"
                  className="nav-link"
                  onClick={() => document.getElementById("departments")?.scrollIntoView()}
                >
                  Departments
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/#how-it-works"
                  className="nav-link"
                  onClick={() => document.getElementById("how-it-works")?.scrollIntoView()}
                >
                  How it works
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/register" className="nav-link">
                  Register
                </NavLink>
              </li>
              <li className="nav-item">
                <Link to="/login" className="btn btn-primary btn-sm px-3">
                  Get Started
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <main className="flex-grow-1">{children}</main>

      <footer className="bg-white border-top py-4">
        <div className="container d-flex flex-column flex-md-row justify-content-between gap-2 text-muted small">
          <div>
            <span className="fw-semibold text-dark">AYUConnect</span> — AI-enabled
            integrated AYUSH healthcare management.
          </div>
          <div>AYUConnect does not provide diagnosis or emergency medical care.</div>
        </div>
      </footer>
    </div>
  );
}

PublicLayout.propTypes = {
  children: PropTypes.node.isRequired,
};
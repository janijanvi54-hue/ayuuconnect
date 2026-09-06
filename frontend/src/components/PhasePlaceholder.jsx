// Shared placeholder used by role dashboards until the corresponding
// backend module is implemented in later phases.
import PropTypes from "prop-types";

export default function PhasePlaceholder({ title, phase, description }) {
  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100">
      <div className="text-center p-4" style={{ maxWidth: "28rem" }}>
        <h1 className="h3 section-title">{title}</h1>
        <p className="text-muted">{description}</p>
        <span className="badge bg-light text-dark border">Planned for {phase}</span>
      </div>
    </div>
  );
}

PhasePlaceholder.propTypes = {
  title: PropTypes.string.isRequired,
  phase: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
};
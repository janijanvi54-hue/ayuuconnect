import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100">
      <div className="text-center p-4">
        <h1 className="display-4 fw-bold">404</h1>
        <p className="text-muted">The page you are looking for does not exist.</p>
        <Link to="/" className="btn btn-primary">
          Back to Home
        </Link>
      </div>
    </div>
  );
}
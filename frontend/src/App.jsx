import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/public/Landing.jsx";
import NotFound from "./pages/public/NotFound.jsx";
import Login from "./pages/auth/Login.jsx";
import Register from "./pages/auth/Register.jsx";
import PatientDashboard from "./pages/patient/Dashboard.jsx";
import DoctorDashboard from "./pages/doctor/Dashboard.jsx";
import AdminDashboard from "./pages/admin/Dashboard.jsx";

// Auth-based route guards (ProtectedRoute / RoleRoute) are wired in
// Phase 3 alongside the authentication APIs. Until then the role pages
// are reachable placeholders behind public paths.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Role dashboard shells (Phase 3 wires real guards) */}
      <Route path="/patient/dashboard" element={<PatientDashboard />} />
      <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />

      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
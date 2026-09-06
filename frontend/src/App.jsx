import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/public/Landing.jsx";
import NotFound from "./pages/public/NotFound.jsx";
import Login from "./pages/auth/Login.jsx";
import Register from "./pages/auth/Register.jsx";
import { RoleRoute, homeFor } from "./components/RouteGuards.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import PropTypes from "prop-types";

import PatientDashboard from "./pages/patient/Dashboard.jsx";
import PatientBook from "./pages/patient/BookAppointment.jsx";
import PatientAppointments from "./pages/patient/Appointments.jsx";
import PatientRecommendations from "./pages/patient/Recommendations.jsx";
import PatientChat from "./pages/patient/Chat.jsx";
import PatientProfile from "./pages/patient/Profile.jsx";

import DoctorDashboard from "./pages/doctor/Dashboard.jsx";
import DoctorAppointments from "./pages/doctor/Appointments.jsx";
import DoctorAvailability from "./pages/doctor/Availability.jsx";
import DoctorPatients from "./pages/doctor/Patients.jsx";

import AdminDashboard from "./pages/admin/Dashboard.jsx";
import AdminUsers from "./pages/admin/Users.jsx";
import AdminDoctors from "./pages/admin/Doctors.jsx";
import AdminDepartments from "./pages/admin/Departments.jsx";
import AdminAudit from "./pages/admin/Audit.jsx";

function PublicOnly({ children }) {
  const { user } = useAuth();
  if (user) return <Navigate to={homeFor(user.role)} replace />;
  return children;
}

PublicOnly.propTypes = {
  children: PropTypes.node.isRequired,
};

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route
        path="/login"
        element={
          <PublicOnly>
            <Login />
          </PublicOnly>
        }
      />
      <Route
        path="/register"
        element={
          <PublicOnly>
            <Register />
          </PublicOnly>
        }
      />

      <Route
        path="/patient/dashboard"
        element={
          <RoleRoute roles={["PATIENT"]}>
            <PatientDashboard />
          </RoleRoute>
        }
      />
      <Route
        path="/patient/book"
        element={
          <RoleRoute roles={["PATIENT"]}>
            <PatientBook />
          </RoleRoute>
        }
      />
      <Route
        path="/patient/appointments"
        element={
          <RoleRoute roles={["PATIENT"]}>
            <PatientAppointments />
          </RoleRoute>
        }
      />
      <Route
        path="/patient/recommendations"
        element={
          <RoleRoute roles={["PATIENT"]}>
            <PatientRecommendations />
          </RoleRoute>
        }
      />
      <Route
        path="/patient/chat"
        element={
          <RoleRoute roles={["PATIENT"]}>
            <PatientChat />
          </RoleRoute>
        }
      />
      <Route
        path="/patient/profile"
        element={
          <RoleRoute roles={["PATIENT"]}>
            <PatientProfile />
          </RoleRoute>
        }
      />

      <Route
        path="/doctor/dashboard"
        element={
          <RoleRoute roles={["DOCTOR"]}>
            <DoctorDashboard />
          </RoleRoute>
        }
      />
      <Route
        path="/doctor/appointments"
        element={
          <RoleRoute roles={["DOCTOR"]}>
            <DoctorAppointments />
          </RoleRoute>
        }
      />
      <Route
        path="/doctor/availability"
        element={
          <RoleRoute roles={["DOCTOR"]}>
            <DoctorAvailability />
          </RoleRoute>
        }
      />
      <Route
        path="/doctor/patients"
        element={
          <RoleRoute roles={["DOCTOR"]}>
            <DoctorPatients />
          </RoleRoute>
        }
      />

      <Route
        path="/admin/dashboard"
        element={
          <RoleRoute roles={["ADMIN"]}>
            <AdminDashboard />
          </RoleRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <RoleRoute roles={["ADMIN"]}>
            <AdminUsers />
          </RoleRoute>
        }
      />
      <Route
        path="/admin/doctors"
        element={
          <RoleRoute roles={["ADMIN"]}>
            <AdminDoctors />
          </RoleRoute>
        }
      />
      <Route
        path="/admin/departments"
        element={
          <RoleRoute roles={["ADMIN"]}>
            <AdminDepartments />
          </RoleRoute>
        }
      />
      <Route
        path="/admin/audit"
        element={
          <RoleRoute roles={["ADMIN"]}>
            <AdminAudit />
          </RoleRoute>
        }
      />

      <Route path="/404" element={<NotFound />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}
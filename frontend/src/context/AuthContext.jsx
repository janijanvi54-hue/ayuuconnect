import { createContext, useContext, useMemo, useState } from "react";
import PropTypes from "prop-types";

// Auth state is wired to the backend in Phase 3 (register/login/logout).
// This provider already exposes the shape the app will use.
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("ayuconnect_user") || "null");
    } catch {
      return null;
    }
  });

  const value = useMemo(
    () => ({
      user,
      setUser,
      login: (token, profile) => {
        localStorage.setItem("ayuconnect_token", token);
        localStorage.setItem("ayuconnect_user", JSON.stringify(profile));
        setUser(profile);
      },
      logout: () => {
        localStorage.removeItem("ayuconnect_token");
        localStorage.removeItem("ayuconnect_user");
        setUser(null);
      },
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return ctx;
}
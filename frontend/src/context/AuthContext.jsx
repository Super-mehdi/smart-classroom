import { useState, useEffect } from "react";
import { AuthContext } from "./authContext";

const API_URL = `http://${window.location.hostname}:8000`;

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem("token")); // Loading if we have a token to verify
  const [error, setError] = useState(null);

  // Fetch current user whenever token changes
  useEffect(() => {
    if (!token) {
      setCurrentUser(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(`${API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error("Token expired");
        return r.json();
      })
      .then((user) => {
        setCurrentUser(user);
        localStorage.setItem("token", token);
      })
      .catch(() => {
        logout();
      })
      .finally(() => {
        setLoading(false);
      });
  }, [token]);

  // Heartbeat effect
  useEffect(() => {
    // ONLY start heartbeat if we have a verified currentUser
    if (!token || !currentUser) return;

    // Immediately send one heartbeat to confirm online status
    fetch(`${API_URL}/api/auth/heartbeat`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }).catch(err => console.error("Initial heartbeat failed", err));

    const interval = setInterval(() => {
      fetch(`${API_URL}/api/auth/heartbeat`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(err => console.error("Heartbeat failed", err));
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [token, !!currentUser]); // Re-run when currentUser becomes truthy

  async function login(email, password) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }
      const { access_token } = await res.json();

      setToken(access_token);
      localStorage.setItem("token", access_token);
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    if (token) {
      try {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (e) {
        console.error("Logout error", e);
      }
    }
    setToken(null);
    setCurrentUser(null);
    localStorage.removeItem("token");
  }

  return (
    <AuthContext.Provider value={{ currentUser, token, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}


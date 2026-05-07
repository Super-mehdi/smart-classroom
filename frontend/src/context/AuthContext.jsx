import { useState, useEffect } from "react";
import { AuthContext } from "./authContext";

const API_URL = "http://localhost:8000";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);       // in memory, not localStorage
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch current user whenever token changes
  useEffect(() => {
  if (!token) return;  // ← just return, don't setState here

  fetch(`${API_URL}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((r) => r.json())
    .then((user) => setCurrentUser(user))
    .catch(() => logout());
}, [token]);

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

    // fetch user immediately before returning
    const userRes = await fetch(`${API_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    const user = await userRes.json();

    setToken(access_token);
    setCurrentUser(user);  // ← set directly, don't wait for useEffect
    return true;
  } catch (err) {
    setError(err.message);
    return false;
  } finally {
    setLoading(false);
  }
}

  function logout() {
    setToken(null);
    setCurrentUser(null);
  }

  return (
    <AuthContext.Provider value={{ currentUser, token, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}


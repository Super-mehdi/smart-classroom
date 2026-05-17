export const API_URL = "http://localhost:8000";

export async function apiFetch(path, options = {}, token = null) {
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function login(email, password) {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function signup({ name, email, password, role }) {
  return apiFetch("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role }),
  });
}

export async function getSessions(token) {
  return apiFetch("/api/analytics/classes/1", {}, token);
}

export async function getSessionDetail(sessionId, token) {
  return apiFetch(`/api/analytics/sessions/${sessionId}`, {}, token);
}

export async function getStudents(token) {
  return apiFetch("/api/students", {}, token);
}

export async function getStudentDetail(studentId, token) {
  return apiFetch(`/api/analytics/students/${studentId}`, {}, token);
}

export async function startSession(classId, token) {
  return apiFetch("/api/sessions/start", {
    method: "POST",
    body: JSON.stringify({ class_id: classId }),
  }, token);
}

export async function stopSession(sessionId, token) {
  return apiFetch(`/api/sessions/${sessionId}/stop`, {
    method: "POST",
  }, token);
}

export async function createUser({ name, email, password, role }, token) {
  return apiFetch("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role }),
  }, token);
}

export async function uploadStudentPhoto(studentId, file, token) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/api/students/${studentId}/photo`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload error: ${res.status}`);
  return res.json();
}
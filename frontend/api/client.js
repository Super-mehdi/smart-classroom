export const API_URL = "http://localhost:8000";

export async function getExample() {
  const res = await fetch(`${API_URL}/example`);
  return res.json();
}
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function AlertConfigPage() {
  const { classId } = useParams();

  // config state
  const [absenceThreshold,   setAbsenceThreshold]   = useState(0.3);
  const [attentionThreshold, setAttentionThreshold] = useState(0.4);
  const [recipientEmails,    setRecipientEmails]    = useState("");
  const [saveStatus,         setSaveStatus]         = useState("");

  // alert history state
  const [alertHistory, setAlertHistory] = useState([]);
  const [sessionId,    setSessionId]    = useState(1); // default session

  // load existing config on mount
  useEffect(() => {
    fetch(`${API}/api/classes/${classId}/alert-config`)
      .then((r) => r.json())
      .then((data) => {
        if (data.absence_threshold !== undefined) {
          setAbsenceThreshold(data.absence_threshold);
          setAttentionThreshold(data.attention_threshold);
          setRecipientEmails((data.recipient_emails || []).join(", "));
        }
      })
      .catch((e) => console.error("Failed to load config:", e));
  }, [classId]);

  // load alert history
  useEffect(() => {
    fetch(`${API}/api/sessions/${sessionId}/alert-history`)
      .then((r) => r.json())
      .then((data) => setAlertHistory(data.alerts || []))
      .catch((e) => console.error("Failed to load alert history:", e));
  }, [sessionId]);

  const handleSave = async () => {
    setSaveStatus("Saving...");
    try {
      const emails = recipientEmails
        .split(",")
        .map((e) => e.trim())
        .filter((e) => e.length > 0);

      const res = await fetch(`${API}/api/classes/${classId}/alert-config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          absence_threshold:   absenceThreshold,
          attention_threshold: attentionThreshold,
          recipient_emails:    emails,
        }),
      });

      if (res.ok) {
        setSaveStatus("Saved ✓");
      } else {
        setSaveStatus("Failed to save");
      }
    } catch (e) {
      setSaveStatus("Error: " + e.message);
    }

    setTimeout(() => setSaveStatus(""), 3000);
  };

  return (
    <div>
      <Navbar />

      <h1>Alert Config — Class {classId}</h1>

      {/* ── Config Form ── */}
      <section>
        <h2>Thresholds</h2>

        <div>
          <label>
            Absence threshold: {Math.round(absenceThreshold * 100)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={absenceThreshold}
            onChange={(e) => setAbsenceThreshold(parseFloat(e.target.value))}
          />
          <small>Alert when more than {Math.round(absenceThreshold * 100)}% of students are absent</small>
        </div>

        <div>
          <label>
            Attention threshold: {attentionThreshold.toFixed(2)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={attentionThreshold}
            onChange={(e) => setAttentionThreshold(parseFloat(e.target.value))}
          />
          <small>Alert when class average attention drops below {attentionThreshold.toFixed(2)}</small>
        </div>

        <div>
          <label>Recipient emails (comma separated)</label>
          <textarea
            rows={3}
            value={recipientEmails}
            onChange={(e) => setRecipientEmails(e.target.value)}
            placeholder="teacher@school.com, admin@school.com"
          />
        </div>

        <button onClick={handleSave}>Save</button>
        {saveStatus && <span> {saveStatus}</span>}
      </section>

      {/* ── Alert History Table ── */}
      <section>
        <h2>Alert History — Session {sessionId}</h2>
        <input
          type="number"
          value={sessionId}
          onChange={(e) => setSessionId(parseInt(e.target.value))}
          placeholder="Session ID"
        />

        {alertHistory.length === 0 ? (
          <p>No alerts fired for this session.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Triggered at</th>
                <th>Threshold</th>
                <th>Value</th>
                <th>Recipients</th>
              </tr>
            </thead>
            <tbody>
              {alertHistory.map((alert) => (
                <tr key={alert._id}>
                  <td>{alert.type}</td>
                  <td>{new Date(alert.triggered_at).toLocaleString()}</td>
                  <td>{alert.threshold}</td>
                  <td>{alert.value}</td>
                  <td>{(alert.recipients || []).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
import React, { useState } from "react";
import styles from "./Sessions.module.css";

const DUMMY_SESSIONS = [
  { id: 1, date: "May 17, 2024", className: "Math 101", duration: "45 min", avgAttention: "82%", attendance: "95%" },
  { id: 2, date: "May 15, 2024", className: "Physics 202", duration: "60 min", avgAttention: "75%", attendance: "88%" },
  { id: 3, date: "May 14, 2024", className: "Math 101", duration: "45 min", avgAttention: "88%", attendance: "100%" },
  { id: 4, date: "May 12, 2024", className: "Computer Science", duration: "90 min", avgAttention: "92%", attendance: "92%" },
  { id: 5, date: "May 10, 2024", className: "Physics 202", duration: "60 min", avgAttention: "70%", attendance: "85%" },
];

const DUMMY_CHART_DATA = Array.from({ length: 61 }, (_, i) => ({
  minute: i,
  score: 0.5 + Math.random() * 0.4,
}));

const DUMMY_STUDENTS = [
  { id: 1, name: "Alice Johnson", status: "Present", score: 0.92 },
  { id: 2, name: "Bob Smith", status: "Present", score: 0.78 },
  { id: 3, name: "Charlie Brown", status: "Absent", score: 0.0 },
  { id: 4, name: "Diana Prince", status: "Present", score: 0.85 },
  { id: 5, name: "Edward Norton", status: "Present", score: 0.65 },
];

export default function Sessions() {
  const [selectedSession, setSelectedSession] = useState(null);

  const handleViewDetails = (session) => {
    setSelectedSession(session);
  };

  const handleBackToList = () => {
    setSelectedSession(null);
  };

  if (selectedSession) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <button className={styles.backBtn} onClick={handleBackToList}>
            <span className="material-icons">arrow_back</span>
          </button>
          <div className={styles.sessionInfo}>
            <h2>{selectedSession.className}</h2>
            <p>{selectedSession.date} • {selectedSession.duration}</p>
          </div>
        </div>

        <div className={styles.summaryGrid}>
          <div className={`${styles.card} ${styles.chartCard}`}>
            <h3>Attention Score over Time</h3>
            <div className={styles.lineChart}>
              <svg viewBox="0 0 600 200" preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
                {/* Grid lines */}
                {[0, 50, 100, 150].map(y => (
                  <line key={y} x1="0" y1={y} x2="600" y2={y} className={styles.chartGrid} />
                ))}
                {/* Data line */}
                <polyline
                  points={DUMMY_CHART_DATA.map(d => `${d.minute * 10},${200 - (d.score * 200)}`).join(' ')}
                  className={styles.chartLine}
                />
                {/* Labels */}
                <text x="0" y="195" className={styles.chartAxis}>0 min</text>
                <text x="560" y="195" className={styles.chartAxis}>60 min</text>
              </svg>
            </div>
          </div>

          <div className={`${styles.card} ${styles.attendanceCard}`}>
            <h3>Attendance Summary</h3>
            <div className={styles.bigPercentage}>{selectedSession.attendance}</div>
            <div className={styles.attendanceCounts}>
              <span>4 Present</span> • <span>1 Absent</span>
            </div>
          </div>
        </div>

        <div className={styles.card}>
          <h3>Student List</h3>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Attention Score</th>
              </tr>
            </thead>
            <tbody>
              {DUMMY_STUDENTS.map(student => (
                <tr key={student.id}>
                  <td>{student.name}</td>
                  <td>
                    <span className={`${styles.badge} ${student.status === 'Present' ? styles.present : styles.absent}`}>
                      {student.status}
                    </span>
                  </td>
                  <td>{student.score > 0 ? (student.score * 100).toFixed(0) + '%' : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Sessions</h1>
      <div className={styles.card}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Date</th>
              <th>Class</th>
              <th>Duration</th>
              <th>Avg Attention</th>
              <th>Attendance Rate</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {DUMMY_SESSIONS.map((session) => (
              <tr key={session.id}>
                <td>{session.date}</td>
                <td>{session.className}</td>
                <td>{session.duration}</td>
                <td>{session.avgAttention}</td>
                <td>{session.attendance}</td>
                <td>
                  <button className={styles.viewBtn} onClick={() => handleViewDetails(session)}>
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

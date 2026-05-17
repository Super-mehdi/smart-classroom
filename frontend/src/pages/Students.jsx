import React, { useState } from "react";
import styles from "./Students.module.css";

const DUMMY_STUDENTS = [
  { id: "S1001", name: "Alice Johnson", attendance: 95, avgAttention: 0.85 },
  { id: "S1002", name: "Bob Smith", attendance: 88, avgAttention: 0.65 },
  { id: "S1003", name: "Charlie Brown", attendance: 72, avgAttention: 0.45 },
  { id: "S1004", name: "Diana Prince", attendance: 100, avgAttention: 0.92 },
  { id: "S1005", name: "Edward Norton", attendance: 60, avgAttention: 0.35 },
  { id: "S1006", name: "Fiona Apple", attendance: 92, avgAttention: 0.78 },
];

const DUMMY_HISTORY = [
  { date: "2024-05-15", class: "Mathematics 101", status: "Present", score: 0.88 },
  { date: "2024-05-14", class: "Physics 202", status: "Present", score: 0.82 },
  { date: "2024-05-13", class: "Mathematics 101", status: "Absent", score: 0 },
  { date: "2024-05-12", class: "Chemistry 303", status: "Present", score: 0.91 },
  { date: "2024-05-11", class: "Mathematics 101", status: "Present", score: 0.85 },
];

const DUMMY_CHART_DATA = [0.75, 0.82, 0.88, 0.85, 0.92];

export default function Students() {
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredStudents = DUMMY_STUDENTS.filter(s => 
    s.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getInitials = (name) => {
    return name.split(" ").map(n => n[0]).join("");
  };

  const getAttentionColor = (score) => {
    if (score >= 0.7) return "#1e8e3e";
    if (score >= 0.4) return "#f9ab00";
    return "#d93025";
  };

  if (selectedStudent) {
    return (
      <div className={styles.container}>
        <button className={styles.backBtn} onClick={() => setSelectedStudent(null)}>
          <span className="material-icons">arrow_back</span>
          Back to Students
        </button>

        <div className={styles.header}>
          <div className={styles.headerInfo}>
            <h2>{selectedStudent.name}</h2>
            <p>Student ID: {selectedStudent.id}</p>
          </div>
        </div>

        <div className={styles.statsRow}>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>Overall Attendance</div>
            <div className={styles.statValue}>{selectedStudent.attendance}%</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>Avg Attention Score</div>
            <div className={styles.statValue}>{selectedStudent.avgAttention}</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>Sessions Attended</div>
            <div className={styles.statValue}>24</div>
          </div>
        </div>

        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Attention Score (Last 5 Sessions)</div>
          <svg width="100%" height="200" viewBox="0 0 500 100" preserveAspectRatio="none">
            <polyline
              fill="none"
              stroke="#1a73e8"
              strokeWidth="2"
              points={DUMMY_CHART_DATA.map((val, i) => `${i * 125},${100 - val * 100}`).join(" ")}
            />
            {DUMMY_CHART_DATA.map((val, i) => (
              <circle
                key={i}
                cx={i * 125}
                cy={100 - val * 100}
                r="3"
                fill="#1a73e8"
              />
            ))}
          </svg>
        </div>

        <div className={styles.historyCard}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Date</th>
                <th>Class</th>
                <th>Status</th>
                <th>Attention Score</th>
              </tr>
            </thead>
            <tbody>
              {DUMMY_HISTORY.map((h, i) => (
                <tr key={i}>
                  <td>{h.date}</td>
                  <td>{h.class}</td>
                  <td className={h.status === "Present" ? styles.statusPresent : styles.statusAbsent}>
                    {h.status}
                  </td>
                  <td>{h.score || "-"}</td>
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
      <h1 className={styles.title}>Students</h1>
      
      <input
        type="text"
        placeholder="Search students..."
        className={styles.searchBar}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <div className={styles.grid}>
        {filteredStudents.map(student => (
          <div key={student.id} className={styles.card}>
            <div className={styles.avatar}>{getInitials(student.name)}</div>
            <h3 className={styles.studentName}>{student.name}</h3>
            <p className={styles.studentId}>ID: {student.id}</p>
            
            <div className={styles.metricRow}>
              <div className={styles.metricLabel}>Attendance: {student.attendance}%</div>
              <div className={styles.progressBar}>
                <div className={styles.progressFill} style={{ width: `${student.attendance}%` }}></div>
              </div>
            </div>

            <div className={styles.metricRow}>
              <div className={styles.metricLabel}>
                <span 
                  className={styles.attentionDot} 
                  style={{ backgroundColor: getAttentionColor(student.avgAttention) }}
                ></span>
                Avg Attention: {student.avgAttention}
              </div>
            </div>

            <button className={styles.viewBtn} onClick={() => setSelectedStudent(student)}>
              View
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

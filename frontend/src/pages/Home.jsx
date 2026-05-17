import React, { useState, useEffect } from "react";
import { useAttentionSocket } from "../hooks/useAttentionSocket";
import { AttentionGauge } from "../components/AttentionGauge";
import { StudentCards } from "../components/StudentCards";
import { useAuth } from "../hooks/useAuth";
import { startSession, stopSession } from "../api/client";
import styles from "./Home.module.css";

export default function Home() {
  const { currentUser, token } = useAuth();
  const [now, setNow] = useState(new Date());
  const [sessionId, setSessionId] = useState(null);
  const scores = useAttentionSocket(sessionId);

  const isTeacher = currentUser?.role === "teacher";
  const userName = currentUser?.full_name || "User";

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatDate = (date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const handleStartSession = async () => {
    try {
      const data = await startSession(1, token);
      setSessionId(data.session_id);
    } catch (error) {
      console.error("Failed to start session:", error);
    }
  };

  const handleEndSession = async () => {
    try {
      await stopSession(sessionId, token);
      setSessionId(null);
    } catch (error) {
      console.error("Failed to stop session:", error);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.leftColumn}>
        {isTeacher ? (
          <div className={styles.card}>
            <h2 className={styles.date}>{formatDate(now)}</h2>
            <div className={styles.time}>{formatTime(now)}</div>
            
            {sessionId ? (
              <button 
                className={`${styles.sessionButton} ${styles.endBtn}`}
                onClick={handleEndSession}
              >
                <span className="material-icons">stop</span>
                End Session
              </button>
            ) : (
              <button 
                className={`${styles.sessionButton} ${styles.startBtn}`}
                onClick={handleStartSession}
              >
                <span className="material-icons">play_arrow</span>
                Start Session
              </button>
            )}
          </div>
        ) : (
          <div className={styles.card}>
            <h1 className={styles.welcomeTitle}>Welcome, {userName}</h1>
            <p className={styles.welcomeSubtitle}>
              Use the Admin panel to manage users and students.
            </p>
          </div>
        )}
      </div>

      <div className={styles.rightColumn}>
        {!sessionId ? (
          <div className={`${styles.card} ${styles.placeholder}`}>
            No active session
          </div>
        ) : (
          <>
            <div className={`${styles.card} ${styles.gaugeContainer}`}>
              <AttentionGauge scores={scores} />
            </div>
            <div className={styles.card}>
              <StudentCards scores={scores} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
import React, { useState, useEffect } from "react";
import { useAttentionSocket } from "../hooks/useAttentionSocket";
import { AttentionGauge } from "../components/AttentionGauge";
import { StudentCards } from "../components/StudentCards";
import { useAuth } from "../hooks/useAuth";
import { useSession } from "../context/SessionContext";
import { apiFetch, startSession, stopSession, startCVPipeline, stopCVPipeline } from "../api/client";

export default function Home() {
  const { currentUser, token } = useAuth();
  const { sessionId, setSessionId } = useSession();
  const [now, setNow] = useState(new Date());
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState("");
  const scores = useAttentionSocket(sessionId);

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (currentUser?.role === "teacher" && token) {
      apiFetch("/api/classes", {}, token).then((data) => {
        setClasses(data);
        if (data.length > 0) setSelectedClassId(data[0].id);
      });
    }
  }, [currentUser, token]);

  const handleStart = async () => {
    const data = await startSession(selectedClassId, token);
    setSessionId(data.session_id);
    await startCVPipeline(data.session_id, token);
  };

  const handleEnd = async () => {
    await stopSession(sessionId, token);
    await stopCVPipeline(sessionId, token);
    setSessionId(null);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-start mb-8">
        <div>
          <div className="text-sm text-gray-500 uppercase tracking-wide">
            {now.toLocaleDateString("en-US", { weekday: "long" })}
          </div>
          <div className="text-3xl font-light text-gray-800">{now.toLocaleDateString("en-US", { month: "long", day: "numeric" })}</div>
          <div className="text-5xl font-thin text-gray-900 mt-1">{now.toLocaleTimeString("en-US", { hour12: false })}</div>
        </div>

        {currentUser?.role === "teacher" && (
            <div className="flex items-center gap-4 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                {!sessionId && (
                  <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" onChange={(e) => setSelectedClassId(e.target.value)}>
                      {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                )}
                <button onClick={sessionId ? handleEnd : handleStart} className={`${sessionId ? "bg-red-500 hover:bg-red-600" : "bg-blue-600 hover:bg-blue-700"} text-white px-6 py-2 rounded-lg flex items-center gap-2 shadow-sm transition-all duration-200 font-medium`}>
                    {sessionId ? "Stop Session" : "Start Session"}
                </button>
            </div>
        )}
      </div>

      {!sessionId ? (
        <div className="border-2 border-dashed border-gray-200 rounded-xl p-16 flex flex-col items-center justify-center text-gray-400">
          <span className="material-icons text-6xl mb-4">pause_circle_outline</span>
          <p className="text-lg">Start a session to see live data</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Class Engagement</h4>
            <AttentionGauge scores={scores} />
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Student Activity</h4>
            <StudentCards scores={scores} />
          </div>
        </div>
      )}
    </div>
  );
}
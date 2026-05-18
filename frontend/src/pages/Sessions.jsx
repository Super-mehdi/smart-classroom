import React, { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { apiFetch } from "../api/client";

export default function Sessions() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [details, setDetails] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const sessionsPerPage = 5;

  useEffect(() => {
    apiFetch("/api/sessions", {}, token).then(data => {
      const sorted = data.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));
      setSessions(sorted);
    });
  }, [token]);

  const handleViewDetails = async (session) => {
    setSelectedSession(session);
    try {
        const data = await apiFetch(`/api/analytics/sessions/${session.session_id}`, {}, token);
        console.log("Raw Session Analytics Data:", data);
        setDetails({
            timeline: data.attention?.timeline || [],
            class_avg: data.attention?.overall_avg || 0,
            attendance: data.attendance || { total: 0, present: 0, absent: 0, summary: [] }
        });
    } catch (e) {
        console.error("Error fetching details", e);
        setDetails({ class_avg: 0, timeline: [], attendance: { total: 0, present: 0, absent: 0, summary: [] } });
    }
  };

  const paginatedSessions = sessions.slice(currentPage * sessionsPerPage, (currentPage + 1) * sessionsPerPage);
  const totalPages = Math.ceil(sessions.length / sessionsPerPage);

  if (selectedSession && details) {
    return (
      <div className="p-6">
        <button className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 font-medium" onClick={() => {setSelectedSession(null); setDetails(null);}}>
          <span className="material-icons">arrow_back</span> Back to Sessions
        </button>
        <div className="flex items-end gap-6 mb-8">
            <h2 className="text-3xl font-light text-gray-900">{selectedSession.class_name || "Class Session"}</h2>
            <p className="text-gray-500 pb-1">{new Date(selectedSession.started_at).toLocaleString()}</p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Attention Score Trend</h3>
            <svg className="w-full h-40" viewBox="0 0 400 100" preserveAspectRatio="none">
              <polyline fill="none" stroke="#2563eb" strokeWidth="2" points={details.timeline?.map((d, i) => `${i * (400/(details.timeline.length||1))},${100 - (d.avg_score||0)*100}`).join(" ")} />
            </svg>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 flex flex-col items-center justify-center">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Class Average</h3>
            <div className="text-4xl font-light text-blue-600">{((details.class_avg||0) * 100).toFixed(0)}%</div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 mt-6 overflow-hidden">
            <div className="p-6 border-b border-gray-100">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Attendance Details</h3>
            </div>
            <table className="w-full text-left">
                <thead className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wide">
                    <tr>
                        <th className="px-6 py-4">Student</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Avg Attention</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {details.attendance.summary?.map(s => (
                        <tr key={s.student_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 font-medium text-gray-800">{s.name}</td>
                            <td className="px-6 py-4"><span className={`rounded-full px-3 py-1 text-xs font-medium ${s.status === 'Present' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>{s.status}</span></td>
                            <td className="px-6 py-4">{(s.score * 100).toFixed(0)}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-normal text-gray-800 mb-6">Sessions</h1>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wide">
            <tr>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Class</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {paginatedSessions.map((s) => (
              <tr key={s.session_id} className="hover:bg-gray-50">
                <td className="px-6 py-4">{new Date(s.started_at).toLocaleString()}</td>
                <td className="px-6 py-4 font-medium text-gray-800">{s.class_name || "Unknown"}</td>
                <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${!s.ended_at ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                        {!s.ended_at ? 'Ongoing' : 'Ended'}
                    </span>
                </td>
                <td className="px-6 py-4">
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium" onClick={() => handleViewDetails(s)}>View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-6 py-4 border-t border-gray-100 flex justify-between items-center">
            <button className="text-sm font-medium text-gray-600 disabled:text-gray-300" disabled={currentPage === 0} onClick={() => setCurrentPage(c => c - 1)}>Previous</button>
            <span className="text-sm text-gray-500">Page {currentPage + 1} of {totalPages || 1}</span>
            <button className="text-sm font-medium text-gray-600 disabled:text-gray-300" disabled={currentPage >= totalPages - 1} onClick={() => setCurrentPage(c => c + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}
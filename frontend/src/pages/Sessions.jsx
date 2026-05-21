import React, { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { apiFetch, getSessionSummary } from "../api/client";

export default function Sessions() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [details, setDetails] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [exportingId, setExportingId] = useState(null);
  const sessionsPerPage = 5;

  useEffect(() => {
    apiFetch("/api/sessions", {}, token).then(data => {
      const sorted = data.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));
      setSessions(sorted);
    });
  }, [token]);

  const handleExportSummary = async (sessionId, className, date) => {
    setExportingId(sessionId);
    try {
      const summaryData = await getSessionSummary(sessionId, token);
      const text = `Session Summary - ${className}\nDate: ${new Date(date).toLocaleString()}\n\nStats:\n- Avg Attention: ${(summaryData.stats.avg_attention * 100).toFixed(0)}%\n- Attendance: ${summaryData.stats.attendance_rate}% (${summaryData.stats.present_students}/${summaryData.stats.total_students})\n\nAI Summary:\n${summaryData.summary_text}`;
      
      const blob = new Blob([text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `session_${sessionId}_summary.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Error exporting summary", e);
      alert("Failed to export summary. Please try again.");
    } finally {
      setExportingId(null);
    }
  };

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
        <div className="flex justify-between items-center mb-6">
          <button className="flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium" onClick={() => {setSelectedSession(null); setDetails(null);}}>
            <span className="material-icons">arrow_back</span> Back to Sessions
          </button>
          <button 
            className="group flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={() => handleExportSummary(selectedSession.session_id, selectedSession.class_name, selectedSession.started_at)}
            disabled={exportingId === selectedSession.session_id}
          >
            <span className={`material-icons text-lg ${exportingId === selectedSession.session_id ? 'animate-spin' : 'group-hover:translate-y-0.5 transition-transform'}`}>
              {exportingId === selectedSession.session_id ? 'sync' : 'auto_awesome'}
            </span>
            <span className="font-semibold tracking-tight">
              {exportingId === selectedSession.session_id ? 'Analyzing...' : 'AI Summary'}
            </span>
          </button>
        </div>
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
                  <div className="flex gap-3 items-center">
                    <button 
                      className="flex items-center gap-1.5 text-blue-600 hover:text-blue-800 text-sm font-semibold transition-colors" 
                      onClick={() => handleViewDetails(s)}
                    >
                      <span className="material-icons text-sm">visibility</span>
                      View
                    </button>
                    <div className="w-px h-4 bg-gray-200"></div>
                    <button 
                      className="flex items-center gap-1.5 text-indigo-600 hover:text-indigo-800 text-sm font-semibold transition-colors disabled:opacity-40" 
                      onClick={() => handleExportSummary(s.session_id, s.class_name, s.started_at)}
                      disabled={exportingId === s.session_id}
                    >
                      <span className={`material-icons text-sm ${exportingId === s.session_id ? 'animate-spin' : ''}`}>
                        {exportingId === s.session_id ? 'sync' : 'auto_awesome'}
                      </span>
                      {exportingId === s.session_id ? '...' : 'AI Summary'}
                    </button>
                  </div>
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
import React, { useState } from "react";

const DUMMY_SESSIONS = [
  { id: 1, date: "May 17, 2024", className: "Math 101", duration: "45 min", avgAttention: "82%", attendance: "95%" },
  { id: 2, date: "May 15, 2024", className: "Physics 202", duration: "60 min", avgAttention: "75%", attendance: "88%" },
  { id: 3, date: "May 14, 2024", className: "Math 101", duration: "45 min", avgAttention: "88%", attendance: "100%" },
  { id: 4, date: "May 12, 2024", className: "Computer Science", duration: "90 min", avgAttention: "92%", attendance: "92%" },
  { id: 5, date: "May 10, 2024", className: "Physics 202", duration: "60 min", avgAttention: "70%", attendance: "85%" },
];

const DUMMY_STUDENTS = [
  { id: 1, name: "Alice Johnson", status: "Present", score: 0.92 },
  { id: 2, name: "Bob Smith", status: "Present", score: 0.78 },
  { id: 3, name: "Charlie Brown", status: "Absent", score: 0.0 },
  { id: 4, name: "Diana Prince", status: "Present", score: 0.85 },
  { id: 5, name: "Edward Norton", status: "Present", score: 0.65 },
];

export default function Sessions() {
  const [selectedSession, setSelectedSession] = useState(null);

  if (selectedSession) {
    return (
      <div className="p-6">
        <button className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 font-medium" onClick={() => setSelectedSession(null)}>
          <span className="material-icons">arrow_back</span> Back to Sessions
        </button>
        <div className="flex items-end gap-6 mb-8">
            <h2 className="text-3xl font-light text-gray-900">{selectedSession.className}</h2>
            <p className="text-gray-500 pb-1">{selectedSession.date} • {selectedSession.duration}</p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Attention Score</h3>
            {/* SVG Chart placeholder */}
            <div className="h-40 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400">Time-series data...</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 flex flex-col items-center justify-center">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Attendance</h3>
            <div className="text-4xl font-light text-blue-600">{selectedSession.attendance}</div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 mt-6">
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wide">
              <tr>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Attention Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {DUMMY_STUDENTS.map(student => (
                <tr key={student.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-800">{student.name}</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${student.status === 'Present' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {student.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">{student.score > 0 ? (student.score * 100).toFixed(0) + '%' : '-'}</td>
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
              <th className="px-6 py-4">Duration</th>
              <th className="px-6 py-4">Avg Attention</th>
              <th className="px-6 py-4">Attendance Rate</th>
              <th className="px-6 py-4">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {DUMMY_SESSIONS.map((session) => (
              <tr key={session.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">{session.date}</td>
                <td className="px-6 py-4 font-medium text-gray-800">{session.className}</td>
                <td className="px-6 py-4">{session.duration}</td>
                <td className="px-6 py-4">{session.avgAttention}</td>
                <td className="px-6 py-4">{session.attendance}</td>
                <td className="px-6 py-4">
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium" onClick={() => setSelectedSession(session)}>
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
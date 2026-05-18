import React, { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { apiFetch } from "../api/client";

export default function Students() {
  const { token } = useAuth();
  const [searchTerm, setSearchTerm] = useState("");
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
        try {
            const list = await apiFetch("/api/students", {}, token);
            const detailed = await Promise.all(list.map(async (s) => {
                const stats = await apiFetch(`/api/analytics/students/${s.id}`, {}, token);
                return { ...s, ...stats };
            }));
            setStudents(detailed);
            setLoading(false);
        } catch (err) {
            setError("Failed to load student data");
            setLoading(false);
        }
    }
    fetchData();
  }, [token]);

  const filtered = students.filter(s => s.name?.toLowerCase().includes(searchTerm.toLowerCase()));

  if (loading) return <div className="p-6">Loading student analytics...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-normal text-gray-800 mb-6">Students</h1>
      <input type="text" placeholder="Search students..." className="w-full border border-gray-200 rounded-lg px-4 py-2 mb-6 focus:outline-none focus:ring-2 focus:ring-blue-500" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
      
      <div className="grid grid-cols-3 gap-4">
        {filtered.map(s => (
          <div key={s.id} className="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition-all duration-200 border border-gray-100">
            <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-medium text-lg mb-3">{s.name?.split(' ').map(n=>n[0]).join('')}</div>
            <h3 className="font-medium text-gray-800">{s.name}</h3>
            <p className="text-sm text-gray-500 mb-4">{s.id}</p>
            
            <div className="space-y-2">
                <div className="text-xs text-gray-500 flex justify-between"><span>Attendance</span><span>{Math.round(s.attendance || 0)}%</span></div>
                <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden"><div className="h-full bg-blue-500" style={{width: `${s.attendance || 0}%`}}></div></div>
                <div className="text-xs text-gray-500 flex justify-between mt-2"><span>Attention</span><span>{(s.avgAttention || 0).toFixed(2)}</span></div>
                <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden"><div className="h-full bg-green-500" style={{width: `${(s.avgAttention || 0)*100}%`}}></div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
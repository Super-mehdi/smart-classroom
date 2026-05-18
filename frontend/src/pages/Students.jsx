import React, { useState } from "react";

const DUMMY_STUDENTS = [
  { id: "S1001", name: "Alice Johnson", attendance: 95, avgAttention: 0.85 },
  { id: "S1002", name: "Bob Smith", attendance: 88, avgAttention: 0.65 },
  { id: "S1003", name: "Charlie Brown", attendance: 72, avgAttention: 0.45 },
  { id: "S1004", name: "Diana Prince", attendance: 100, avgAttention: 0.92 },
  { id: "S1005", name: "Edward Norton", attendance: 60, avgAttention: 0.35 },
  { id: "S1006", name: "Fiona Apple", attendance: 92, avgAttention: 0.78 },
];

export default function Students() {
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = DUMMY_STUDENTS.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="p-6">
      <h1 className="text-2xl font-normal text-gray-800 mb-6">Students</h1>
      <input type="text" placeholder="Search students..." className="w-full border border-gray-200 rounded-lg px-4 py-2 mb-6 focus:outline-none focus:ring-2 focus:ring-blue-500" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
      
      <div className="grid grid-cols-3 gap-4">
        {filtered.map(s => (
          <div key={s.id} className="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition-all duration-200 border border-gray-100">
            <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-medium text-lg mb-3">{s.name.split(' ').map(n=>n[0]).join('')}</div>
            <h3 className="font-medium text-gray-800">{s.name}</h3>
            <p className="text-sm text-gray-500 mb-4">{s.id}</p>
            
            <div className="space-y-2">
                <div className="text-xs text-gray-500 flex justify-between"><span>Attendance</span><span>{s.attendance}%</span></div>
                <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden"><div className="h-full bg-blue-500" style={{width: `${s.attendance}%`}}></div></div>
                <div className="text-xs text-gray-500 flex justify-between mt-2"><span>Attention</span><span>{s.avgAttention}</span></div>
                <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden"><div className="h-full bg-green-500" style={{width: `${s.avgAttention*100}%`}}></div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
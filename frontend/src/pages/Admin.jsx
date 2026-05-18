import React, { useState, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';

const DUMMY_USERS = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'teacher', createdAt: '2024-05-10' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'superuser', createdAt: '2024-05-12' },
];

const DUMMY_STUDENTS = [
  { id: 'S1001', name: 'Alice Johnson', enrolled: true },
  { id: 'S1002', name: 'Bob Smith', enrolled: false },
];

export default function Admin() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState(DUMMY_USERS);
  const [students, setStudents] = useState(DUMMY_STUDENTS);

  const [userForm, setUserForm] = useState({ name: '', email: '', password: '', role: 'teacher' });
  const [studentForm, setStudentForm] = useState({ name: '', id: '' });
  const fileInputRef = useRef(null);
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  if (currentUser?.role !== 'superuser') return <div className="p-8 text-red-500">Unauthorized Access</div>;

  const handleCreateUser = (e) => {
    e.preventDefault();
    setUsers([...users, { ...userForm, id: users.length + 1, createdAt: new Date().toISOString().split('T')[0] }]);
    setUserForm({ name: '', email: '', password: '', role: 'teacher' });
  };

  const handleAddStudent = (e) => {
    e.preventDefault();
    setStudents([...students, { ...studentForm, enrolled: false }]);
    setStudentForm({ name: '', id: '' });
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-normal text-gray-800 mb-6">Admin Dashboard</h1>
      
      <div className="flex gap-6 border-b border-gray-200 mb-6">
        {['users', 'students'].map(tab => (
            <button key={tab} className={`pb-3 capitalize ${activeTab === tab ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`} onClick={() => setActiveTab(tab)}>
                {tab}
            </button>
        ))}
      </div>

      {activeTab === 'users' && (
        <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 max-w-md">
              <h2 className="text-lg font-medium mb-6">Create New User</h2>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <input className="w-full border-b-2 border-gray-200 focus:border-blue-500 outline-none py-2" placeholder="Full Name" value={userForm.name} onChange={(e) => setUserForm({...userForm, name: e.target.value})} required />
                <input className="w-full border-b-2 border-gray-200 focus:border-blue-500 outline-none py-2" placeholder="Email" value={userForm.email} onChange={(e) => setUserForm({...userForm, email: e.target.value})} required />
                <input className="w-full border-b-2 border-gray-200 focus:border-blue-500 outline-none py-2" type="password" placeholder="Password" value={userForm.password} onChange={(e) => setUserForm({...userForm, password: e.target.value})} required />
                <select className="w-full border-b-2 border-gray-200 focus:border-blue-500 outline-none py-2 bg-transparent" value={userForm.role} onChange={(e) => setUserForm({...userForm, role: e.target.value})}>
                    <option value="teacher">Teacher</option>
                    <option value="superuser">Superuser</option>
                </select>
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg mt-4">Create User</button>
              </form>
            </div>
        </div>
      )}

      {activeTab === 'students' && (
        <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                <form onSubmit={handleAddStudent} className="flex gap-4">
                    <input className="flex-1 border border-gray-200 rounded-lg px-4 py-2" placeholder="Name" value={studentForm.name} onChange={(e) => setStudentForm({...studentForm, name: e.target.value})} required />
                    <input className="flex-1 border border-gray-200 rounded-lg px-4 py-2" placeholder="ID" value={studentForm.id} onChange={(e) => setStudentForm({...studentForm, id: e.target.value})} required />
                    <button className="bg-blue-600 text-white px-6 py-2 rounded-lg">Add Student</button>
                </form>
            </div>
            <div className="grid grid-cols-3 gap-4">
                {students.map(s => (
                    <div key={s.id} className="bg-white rounded-xl shadow-sm p-5 border border-gray-100 flex justify-between items-center">
                        <div>
                            <h3 className="font-medium text-gray-800">{s.name}</h3>
                            <p className="text-sm text-gray-500">{s.id}</p>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                            <span className={`px-3 py-1 rounded-full text-xs ${s.enrolled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>{s.enrolled ? 'Enrolled' : 'Not Enrolled'}</span>
                            <button onClick={() => {setSelectedStudentId(s.id); fileInputRef.current.click()}} className="text-blue-600 hover:bg-blue-50 text-sm border border-blue-600 rounded-lg px-3 py-1">Upload Photo</button>
                        </div>
                    </div>
                ))}
            </div>
            <input type="file" ref={fileInputRef} className="hidden" onChange={(e) => e.target.files && setStudents(students.map(s => s.id === selectedStudentId ? {...s, enrolled: true} : s))} accept="image/*" />
        </div>
      )}
    </div>
  );
}
import React, { useState, useRef } from 'react';
import styles from './Admin.module.css';
import { useAuth } from '../hooks/useAuth';

const DUMMY_USERS = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'teacher', createdAt: '2024-05-10' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'superuser', createdAt: '2024-05-12' },
  { id: 3, name: 'Robert Brown', email: 'robert@example.com', role: 'teacher', createdAt: '2024-05-15' },
];

const DUMMY_STUDENTS = [
  { id: 'S1001', name: 'Alice Johnson', enrolled: true },
  { id: 'S1002', name: 'Bob Smith', enrolled: false },
  { id: 'S1003', name: 'Charlie Brown', enrolled: true },
  { id: 'S1004', name: 'Diana Prince', enrolled: false },
  { id: 'S1005', name: 'Edward Norton', enrolled: false },
];

export default function Admin() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('users'); // 'users' or 'students'
  const [users, setUsers] = useState(DUMMY_USERS);
  const [students, setStudents] = useState(DUMMY_STUDENTS);

  // Form states
  const [userForm, setUserForm] = useState({ name: '', email: '', password: '', role: 'teacher' });
  const [studentForm, setStudentForm] = useState({ name: '', id: '' });

  const fileInputRef = useRef(null);
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  if (currentUser?.role !== 'superuser') {
    return <div className={styles.unauthorized}>Unauthorized Access</div>;
  }

  const handleCreateUser = (e) => {
    e.preventDefault();
    const newUser = {
      ...userForm,
      id: users.length + 1,
      createdAt: new Date().toISOString().split('T')[0],
    };
    setUsers([...users, newUser]);
    setUserForm({ name: '', email: '', password: '', role: 'teacher' });
  };

  const handleAddStudent = (e) => {
    e.preventDefault();
    const newStudent = {
      id: studentForm.id,
      name: studentForm.name,
      enrolled: false,
    };
    setStudents([...students, newStudent]);
    setStudentForm({ name: '', id: '' });
  };

  const handleUploadPhoto = (studentId) => {
    setSelectedStudentId(studentId);
    fileInputRef.current.click();
  };

  const onFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setStudents(prev => prev.map(s => 
        s.id === selectedStudentId ? { ...s, enrolled: true } : s
      ));
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>Admin Dashboard</h1>
      
      <div className={styles.tabs}>
        <button 
          className={`${styles.tab} ${activeTab === 'users' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Create User
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'students' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('students')}
        >
          Enroll Students
        </button>
      </div>

      <div className={styles.tabContent}>
        {activeTab === 'users' && (
          <div className={styles.section}>
            <div className={styles.card}>
              <h2 className={styles.cardTitle}>Create New User</h2>
              <form onSubmit={handleCreateUser} className={styles.form}>
                <div className={styles.formGroup}>
                  <label>Name</label>
                  <input 
                    type="text" 
                    value={userForm.name}
                    onChange={(e) => setUserForm({...userForm, name: e.target.value})}
                    required 
                    placeholder="Full Name"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Email</label>
                  <input 
                    type="email" 
                    value={userForm.email}
                    onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                    required 
                    placeholder="email@example.com"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Password</label>
                  <input 
                    type="password" 
                    value={userForm.password}
                    onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                    required 
                    placeholder="••••••••"
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Role</label>
                  <select 
                    value={userForm.role}
                    onChange={(e) => setUserForm({...userForm, role: e.target.value})}
                  >
                    <option value="teacher">teacher</option>
                    <option value="superuser">superuser</option>
                  </select>
                </div>
                <button type="submit" className={styles.primaryButton}>Create User</button>
              </form>
            </div>

            <div className={`${styles.card} ${styles.tableCard}`}>
              <h2 className={styles.cardTitle}>Existing Users</h2>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td><span className={`${styles.roleBadge} ${styles[user.role]}`}>{user.role}</span></td>
                      <td>{user.createdAt}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'students' && (
          <div className={styles.section}>
            <div className={styles.card}>
              <h2 className={styles.cardTitle}>Create Student</h2>
              <form onSubmit={handleAddStudent} className={`${styles.form} ${styles.inlineForm}`}>
                <div className={styles.formGroup}>
                  <input 
                    type="text" 
                    value={studentForm.name}
                    onChange={(e) => setStudentForm({...studentForm, name: e.target.value})}
                    required 
                    placeholder="Student Name"
                  />
                </div>
                <div className={styles.formGroup}>
                  <input 
                    type="text" 
                    value={studentForm.id}
                    onChange={(e) => setStudentForm({...studentForm, id: e.target.value})}
                    required 
                    placeholder="Student ID"
                  />
                </div>
                <button type="submit" className={styles.primaryButton}>Add Student</button>
              </form>
            </div>

            <div className={styles.studentGrid}>
              {students.map(student => (
                <div key={student.id} className={styles.studentCard}>
                  <div className={styles.studentInfo}>
                    <h3>{student.name}</h3>
                    <p>ID: {student.id}</p>
                  </div>
                  <div className={styles.studentActions}>
                    <span className={`${styles.statusBadge} ${student.enrolled ? styles.enrolled : styles.notEnrolled}`}>
                      {student.enrolled ? 'Enrolled' : 'Not Enrolled'}
                    </span>
                    <button 
                      onClick={() => handleUploadPhoto(student.id)}
                      className={styles.uploadButton}
                    >
                      <span className="material-icons">photo_camera</span>
                      Upload Photo
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={onFileChange}
              accept="image/*"
            />
          </div>
        )}
      </div>
    </div>
  );
}

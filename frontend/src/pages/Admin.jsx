import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiFetch, API_URL } from '../api/client';
import styles from './Admin.module.css';

export default function Admin() {
  const { currentUser, token } = useAuth();
  const [activeTab, setActiveTab] = useState('users'); // 'users' or 'students'
  
  // Users state
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [userFormData, setUserFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'teacher',
    department: '',
  });

  // Students state
  const [students, setStudents] = useState([]);
  const [studentsLoading, setStudentsLoading] = useState(true);
  const [editingStudent, setEditingStudent] = useState(null);
  const [studentFormData, setStudentFormData] = useState({
    id: '',
    name: '',
    photo: null,
  });

  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch users
  const fetchUsers = async () => {
    try {
      const data = await apiFetch('/api/users', {}, token);
      setUsers(data);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    } finally {
      setUsersLoading(false);
    }
  };

  // Fetch students
  const fetchStudents = async () => {
    try {
      const data = await apiFetch('/api/students', {}, token);
      setStudents(data);
    } catch (err) {
      console.error('Failed to fetch students:', err);
    } finally {
      setStudentsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUsers();
      fetchStudents();

      // Poll for users every 15 seconds to keep "Online Now" accurate
      const interval = setInterval(fetchUsers, 15000);
      return () => clearInterval(interval);
    }
  }, [token]);

  // Reset forms
  const resetUserForm = () => {
    setUserFormData({
      full_name: '',
      email: '',
      password: '',
      role: 'teacher',
      department: '',
    });
    setEditingUser(null);
    setFormError('');
    setFormSuccess('');
  };

  const resetStudentForm = () => {
    setStudentFormData({
      id: '',
      name: '',
      photo: null,
    });
    setEditingStudent(null);
    setFormError('');
    setFormSuccess('');
    // Clear file input
    const fileInput = document.getElementById('student-photo');
    if (fileInput) fileInput.value = '';
  };

  // Handle edit click
  const handleEditUser = (user) => {
    setEditingUser(user);
    setUserFormData({
      full_name: user.full_name || '',
      email: user.email || '',
      password: '',
      role: user.role || 'teacher',
      department: user.department || '',
    });
    setFormError('');
    setFormSuccess('');
  };

  const handleEditStudent = (student) => {
    setEditingStudent(student);
    setStudentFormData({
      id: student.id,
      name: student.name,
      photo: null,
    });
    setFormError('');
    setFormSuccess('');
  };

  // Handle User Submit
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');
    setSubmitting(true);

    try {
      if (editingUser) {
        const payload = { ...userFormData };
        if (!payload.password) delete payload.password;
        await apiFetch(`/api/users/${editingUser.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        }, token);
        setFormSuccess('User updated successfully');
      } else {
        if (!userFormData.password) {
          setFormError('Password is required for new users');
          setSubmitting(false);
          return;
        }
        
        const generatedOfficeNumber = 'OFFICE-' + Math.floor(1000 + Math.random() * 9000);
        const createPayload = {
            ...userFormData,
            office_number: generatedOfficeNumber
        };
        
        await apiFetch('/api/users', {
          method: 'POST',
          body: JSON.stringify(createPayload),
        }, token);
        setFormSuccess('User created successfully');
      }
      await fetchUsers();
      setTimeout(resetUserForm, 1500);
    } catch (err) {
      setFormError(err.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle Student Submit
  const handleStudentSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');
    setSubmitting(true);

    try {
      const formData = new FormData();
      if (editingStudent) {
        if (studentFormData.name) formData.append('name', studentFormData.name);
        if (studentFormData.photo) formData.append('photo', studentFormData.photo);
        
        const res = await fetch(`${API_URL}/api/students/${editingStudent.id}`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        if (!res.ok) throw new Error('Failed to update student');
        setFormSuccess('Student updated successfully');
      } else {
        if (!studentFormData.photo) {
            setFormError('Photo is required for new students');
            setSubmitting(false);
            return;
        }
        formData.append('student_id', studentFormData.id);
        formData.append('name', studentFormData.name);
        formData.append('photo', studentFormData.photo);

        const res = await fetch(`${API_URL}/api/students`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || 'Failed to create student');
        }
        setFormSuccess('Student enrolled successfully');
      }
      await fetchStudents();
      setTimeout(resetStudentForm, 1500);
    } catch (err) {
      setFormError(err.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle delete
  const handleDeleteUser = async (userId) => {
    try {
      await apiFetch(`/api/users/${userId}`, { method: 'DELETE' }, token);
      setDeleteConfirm(null);
      await fetchUsers();
    } catch (err) {
      console.error('Delete user failed:', err);
    }
  };

  const handleDeleteStudent = async (studentId) => {
    try {
      await apiFetch(`/api/students/${studentId}`, { method: 'DELETE' }, token);
      setDeleteConfirm(null);
      await fetchStudents();
    } catch (err) {
      console.error('Delete student failed:', err);
    }
  };

  if (currentUser?.role !== 'superuser') {
    return <div className={styles.unauthorized}>
      <span className="material-icons" style={{ fontSize: 48, marginBottom: 12 }}>lock</span>
      <p>Unauthorized Access</p>
    </div>;
  }

  const filteredUsers = users.filter(u =>
    u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredStudents = students.filter(s =>
    s.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalUsers = users.length;
  const onlineUsers = users.filter(u => u.is_online).length;
  const teacherCount = users.filter(u => u.role === 'teacher').length;
  const totalStudents = students.length;

  return (
    <div className={styles.container}>
      {/* Stats Row */}
      <div className={styles.statsRow}>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: '#e8f0fe', color: '#1a73e8' }}>
            <span className="material-icons">group</span>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statValue}>{totalUsers}</span>
            <span className={styles.statLabel}>Total Users</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: '#e6f4ea', color: '#1e8e3e' }}>
            <span className="material-icons">circle</span>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statValue}>{onlineUsers}</span>
            <span className={styles.statLabel}>Online Now</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: '#fef7e0', color: '#f9ab00' }}>
            <span className="material-icons">school</span>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statValue}>{teacherCount}</span>
            <span className={styles.statLabel}>Teachers</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: '#fce8e6', color: '#d93025' }}>
            <span className="material-icons">face</span>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statValue}>{totalStudents}</span>
            <span className={styles.statLabel}>Students</span>
          </div>
        </div>
      </div>

      {/* Tab Selector */}
      <div className={styles.tabContainer}>
        <button 
          className={`${styles.tabLink} ${activeTab === 'users' ? styles.activeTab : ''}`}
          onClick={() => { setActiveTab('users'); setSearchTerm(''); setFormError(''); setFormSuccess(''); }}
        >
          <span className="material-icons">manage_accounts</span>
          User Management
        </button>
        <button 
          className={`${styles.tabLink} ${activeTab === 'students' ? styles.activeTab : ''}`}
          onClick={() => { setActiveTab('students'); setSearchTerm(''); setFormError(''); setFormSuccess(''); }}
        >
          <span className="material-icons">person_add_alt</span>
          Student Enrollment
        </button>
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* Left Panel: Form */}
        <div className={styles.formPanel}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 className={styles.cardTitle}>
                {activeTab === 'users' 
                  ? (editingUser ? 'Edit User' : 'Create New User')
                  : (editingStudent ? 'Edit Student' : 'Enroll New Student')
                }
              </h2>
              {(editingUser || editingStudent) && (
                <button className={styles.cancelEditBtn} onClick={activeTab === 'users' ? resetUserForm : resetStudentForm}>
                  <span className="material-icons" style={{ fontSize: 18 }}>close</span>
                  Cancel
                </button>
              )}
            </div>

            {formError && (
              <div className={styles.alert + ' ' + styles.alertError}>
                <span className="material-icons" style={{ fontSize: 18 }}>error_outline</span>
                {formError}
              </div>
            )}

            {formSuccess && (
              <div className={styles.alert + ' ' + styles.alertSuccess}>
                <span className="material-icons" style={{ fontSize: 18 }}>check_circle_outline</span>
                {formSuccess}
              </div>
            )}

            {activeTab === 'users' ? (
              <form onSubmit={handleUserSubmit} className={styles.form}>
                <div className={styles.formGroup}>
                  <label>Full Name</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">person</span>
                    <input
                      type="text"
                      placeholder="Enter full name"
                      value={userFormData.full_name}
                      onChange={(e) => setUserFormData({ ...userFormData, full_name: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Email Address</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">email</span>
                    <input
                      type="email"
                      placeholder="Enter email address"
                      value={userFormData.email}
                      onChange={(e) => setUserFormData({ ...userFormData, email: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Password {editingUser && <span className={styles.optionalLabel}>(leave blank to keep current)</span>}</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">lock</span>
                    <input
                      type="password"
                      placeholder={editingUser ? 'Leave blank to keep current' : 'Enter password'}
                      value={userFormData.password}
                      onChange={(e) => setUserFormData({ ...userFormData, password: e.target.value })}
                      required={!editingUser}
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Role</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">badge</span>
                    <select
                      value={userFormData.role}
                      onChange={(e) => setUserFormData({ ...userFormData, role: e.target.value })}
                    >
                      <option value="teacher">Teacher</option>
                      <option value="superuser">Superuser</option>
                    </select>
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Department</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">business</span>
                    <input
                      type="text"
                      placeholder="e.g. Computer Science"
                      value={userFormData.department}
                      onChange={(e) => setUserFormData({ ...userFormData, department: e.target.value })}
                    />
                  </div>
                </div>

                <button type="submit" className={styles.submitBtn} disabled={submitting}>
                  {submitting ? (
                    <><span className={styles.spinner}></span> Processing...</>
                  ) : (
                    <><span className="material-icons" style={{ fontSize: 20 }}>{editingUser ? 'save' : 'person_add'}</span>
                    {editingUser ? 'Update User' : 'Create User'}</>
                  )}
                </button>
              </form>
            ) : (
              <form onSubmit={handleStudentSubmit} className={styles.form}>
                <div className={styles.formGroup}>
                  <label>Student ID</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">fingerprint</span>
                    <input
                      type="text"
                      placeholder="e.g. S001"
                      value={studentFormData.id}
                      onChange={(e) => setStudentFormData({ ...studentFormData, id: e.target.value })}
                      required
                      disabled={!!editingStudent}
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Student Name</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">person</span>
                    <input
                      type="text"
                      placeholder="Enter student name"
                      value={studentFormData.name}
                      onChange={(e) => setStudentFormData({ ...studentFormData, name: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label>Photo {editingStudent && <span className={styles.optionalLabel}>(leave blank to keep current)</span>}</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">add_a_photo</span>
                    <input
                      id="student-photo"
                      type="file"
                      accept="image/*"
                      onChange={(e) => setStudentFormData({ ...studentFormData, photo: e.target.files[0] })}
                      required={!editingStudent}
                    />
                  </div>
                </div>

                <button type="submit" className={styles.submitBtn} disabled={submitting}>
                  {submitting ? (
                    <><span className={styles.spinner}></span> Processing...</>
                  ) : (
                    <><span className="material-icons" style={{ fontSize: 20 }}>{editingStudent ? 'save' : 'person_add'}</span>
                    {editingStudent ? 'Update Student' : 'Enroll Student'}</>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Right Panel: Table */}
        <div className={styles.tablePanel}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 className={styles.cardTitle}>{activeTab === 'users' ? 'Users' : 'Students'}</h2>
              <div className={styles.searchWrapper}>
                <span className="material-icons">search</span>
                <input
                  type="text"
                  placeholder={`Search ${activeTab}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {activeTab === 'users' ? (
              usersLoading ? (
                <div className={styles.loadingState}><span className={styles.spinner + ' ' + styles.spinnerLarge}></span><p>Loading users...</p></div>
              ) : filteredUsers.length === 0 ? (
                <div className={styles.emptyState}><span className="material-icons" style={{ fontSize: 48, color: '#dadce0' }}>person_off</span><p>No users found</p></div>
              ) : (
                <div className={styles.tableWrapper}>
                  <table className={styles.table}>
                    <thead>
                      <tr><th>User</th><th>Role</th><th>Department</th><th>Status</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((user) => (
                        <tr key={user.id} className={editingUser?.id === user.id ? styles.editingRow : ''}>
                          <td>
                            <div className={styles.userCell}>
                              <div className={styles.userAvatar} style={{ background: user.role === 'superuser' ? '#fef7e0' : '#e8f0fe', color: user.role === 'superuser' ? '#f9ab00' : '#1a73e8' }}>
                                {user.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                              </div>
                              <div className={styles.userInfo}>
                                <span className={styles.userName}>{user.full_name}</span>
                                <span className={styles.userEmail}>{user.email}</span>
                              </div>
                            </div>
                          </td>
                          <td><span className={`${styles.roleBadge} ${styles[user.role]}`}>{user.role === 'superuser' ? 'Admin' : 'Teacher'}</span></td>
                          <td><span className={styles.departmentText}>{user.department || '—'}</span></td>
                          <td>
                            <div className={styles.statusCell}>
                              <span className={`${styles.statusDot} ${user.is_online ? styles.online : styles.offline}`}></span>
                              <span className={user.is_online ? styles.statusOnline : styles.statusOffline}>{user.is_online ? 'Online' : 'Offline'}</span>
                            </div>
                          </td>
                          <td>
                            <div className={styles.actionButtons}>
                              <button className={styles.editBtn} onClick={() => handleEditUser(user)} title="Edit user"><span className="material-icons">edit</span></button>
                              {deleteConfirm === user.id ? (
                                <div className={styles.deleteConfirmGroup}>
                                  <button className={styles.confirmDeleteBtn} onClick={() => handleDeleteUser(user.id)} title="Confirm delete"><span className="material-icons">check</span></button>
                                  <button className={styles.cancelDeleteBtn} onClick={() => setDeleteConfirm(null)} title="Cancel"><span className="material-icons">close</span></button>
                                </div>
                              ) : (
                                <button className={styles.deleteBtn} onClick={() => setDeleteConfirm(user.id)} title="Delete user"><span className="material-icons">delete_outline</span></button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            ) : (
              studentsLoading ? (
                <div className={styles.loadingState}><span className={styles.spinner + ' ' + styles.spinnerLarge}></span><p>Loading students...</p></div>
              ) : filteredStudents.length === 0 ? (
                <div className={styles.emptyState}><span className="material-icons" style={{ fontSize: 48, color: '#dadce0' }}>face</span><p>No students enrolled</p></div>
              ) : (
                <div className={styles.tableWrapper}>
                  <table className={styles.table}>
                    <thead>
                      <tr><th>Student</th><th>ID</th><th>Enrolled</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {filteredStudents.map((student) => (
                        <tr key={student.id} className={editingStudent?.id === student.id ? styles.editingRow : ''}>
                          <td>
                            <div className={styles.userCell}>
                              <div className={styles.userAvatar} style={{ background: '#e6f4ea', color: '#1e8e3e' }}>
                                <span className="material-icons" style={{ fontSize: 18 }}>person</span>
                              </div>
                              <div className={styles.userInfo}>
                                <span className={styles.userName}>{student.name}</span>
                              </div>
                            </div>
                          </td>
                          <td><span className={styles.departmentText}>{student.id}</span></td>
                          <td>
                            <span className={styles.dateText}>
                              {new Date(student.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                            </span>
                          </td>
                          <td>
                            <div className={styles.actionButtons}>
                              <button className={styles.editBtn} onClick={() => handleEditStudent(student)} title="Edit student"><span className="material-icons">edit</span></button>
                              {deleteConfirm === student.id ? (
                                <div className={styles.deleteConfirmGroup}>
                                  <button className={styles.confirmDeleteBtn} onClick={() => handleDeleteStudent(student.id)} title="Confirm delete"><span className="material-icons">check</span></button>
                                  <button className={styles.cancelDeleteBtn} onClick={() => setDeleteConfirm(null)} title="Cancel"><span className="material-icons">close</span></button>
                                </div>
                              ) : (
                                <button className={styles.deleteBtn} onClick={() => setDeleteConfirm(student.id)} title="Delete student"><span className="material-icons">delete_outline</span></button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}

            <div className={styles.tableFooter}>
              <span className={styles.resultCount}>
                Showing {activeTab === 'users' ? filteredUsers.length : filteredStudents.length} results
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
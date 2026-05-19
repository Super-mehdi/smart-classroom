import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiFetch } from '../api/client';
import styles from './Admin.module.css';

export default function Admin() {
  const { currentUser, token } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'teacher',
    department: '',
    office_number: '',
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
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchUsers();
  }, [token]);

  // Reset form
  const resetForm = () => {
    setFormData({
      full_name: '',
      email: '',
      password: '',
      role: 'teacher',
      department: '',
      office_number: '',
    });
    setEditingUser(null);
    setFormError('');
    setFormSuccess('');
  };

  // Handle edit click
  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      full_name: user.full_name || '',
      email: user.email || '',
      password: '',
      role: user.role || 'teacher',
      department: user.department || '',
      office_number: user.office_number || '',
    });
    setFormError('');
    setFormSuccess('');
  };

  // Handle submit (create or update)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');
    setSubmitting(true);

    try {
      if (editingUser) {
        // Update
        const payload = { ...formData };
        if (!payload.password) delete payload.password;
        await apiFetch(`/api/users/${editingUser.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        }, token);
        setFormSuccess('User updated successfully');
      } else {
        // Create
        if (!formData.password) {
          setFormError('Password is required for new users');
          setSubmitting(false);
          return;
        }
        
        // Auto-generate office number as requested
        const generatedOfficeNumber = 'OFFICE-' + Math.floor(1000 + Math.random() * 9000);
        const createPayload = {
            ...formData,
            office_number: generatedOfficeNumber
        };
        
        await apiFetch('/api/users', {
          method: 'POST',
          body: JSON.stringify(createPayload),
        }, token);
        setFormSuccess('User created successfully');
      }
      await fetchUsers();
      setTimeout(() => {
        resetForm();
      }, 1500);
    } catch (err) {
      setFormError(err.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle delete
  const handleDelete = async (userId) => {
    try {
      await apiFetch(`/api/users/${userId}`, { method: 'DELETE' }, token);
      setDeleteConfirm(null);
      await fetchUsers();
    } catch (err) {
      console.error('Delete failed:', err);
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

  const totalUsers = users.length;
  const onlineUsers = users.filter(u => u.is_online).length;
  const teacherCount = users.filter(u => u.role === 'teacher').length;
  const adminCount = users.filter(u => u.role === 'superuser').length;

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
            <span className="material-icons">admin_panel_settings</span>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statValue}>{adminCount}</span>
            <span className={styles.statLabel}>Admins</span>
          </div>
        </div>
      </div>

      {/* Main Content: Form + Table */}
      <div className={styles.mainContent}>
        {/* Left Panel: CRUD Form */}
        <div className={styles.formPanel}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 className={styles.cardTitle}>
                {editingUser ? 'Edit User' : 'Create New User'}
              </h2>
              {editingUser && (
                <button className={styles.cancelEditBtn} onClick={resetForm}>
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

            <form onSubmit={handleSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <label>Full Name</label>
                <div className={styles.inputWrapper}>
                  <span className="material-icons">person</span>
                  <input
                    type="text"
                    placeholder="Enter full name"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
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
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required={!editingUser}
                  />
                </div>
              </div>

              <div className={styles.formGroup}>
                <label>Role</label>
                <div className={styles.inputWrapper}>
                  <span className="material-icons">badge</span>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  >
                    <option value="teacher">Teacher</option>
                    <option value="superuser">Superuser</option>
                  </select>
                </div>
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Department</label>
                  <div className={styles.inputWrapper}>
                    <span className="material-icons">business</span>
                    <input
                      type="text"
                      placeholder="e.g. Computer Science"
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              <button type="submit" className={styles.submitBtn} disabled={submitting}>
                {submitting ? (
                  <>
                    <span className={styles.spinner}></span>
                    {editingUser ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  <>
                    <span className="material-icons" style={{ fontSize: 20 }}>
                      {editingUser ? 'save' : 'person_add'}
                    </span>
                    {editingUser ? 'Update User' : 'Create User'}
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Right Panel: Users Table */}
        <div className={styles.tablePanel}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 className={styles.cardTitle}>Users</h2>
              <div className={styles.searchWrapper}>
                <span className="material-icons">search</span>
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {loading ? (
              <div className={styles.loadingState}>
                <span className={styles.spinner + ' ' + styles.spinnerLarge}></span>
                <p>Loading users...</p>
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className={styles.emptyState}>
                <span className="material-icons" style={{ fontSize: 48, color: '#dadce0' }}>person_off</span>
                <p>No users found</p>
              </div>
            ) : (
              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Role</th>
                      <th>Department</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className={editingUser?.id === user.id ? styles.editingRow : ''}>
                        <td>
                          <div className={styles.userCell}>
                            <div className={styles.userAvatar} style={{
                              background: user.role === 'superuser' ? '#fef7e0' : '#e8f0fe',
                              color: user.role === 'superuser' ? '#f9ab00' : '#1a73e8',
                            }}>
                              {user.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                            </div>
                            <div className={styles.userInfo}>
                              <span className={styles.userName}>{user.full_name}</span>
                              <span className={styles.userEmail}>{user.email}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`${styles.roleBadge} ${styles[user.role]}`}>
                            {user.role === 'superuser' ? 'Admin' : 'Teacher'}
                          </span>
                        </td>
                        <td>
                          <span className={styles.departmentText}>
                            {user.department || '—'}
                          </span>
                        </td>
                        <td>
                          <div className={styles.statusCell}>
                            <span className={`${styles.statusDot} ${user.is_online ? styles.online : styles.offline}`}></span>
                            <span className={user.is_online ? styles.statusOnline : styles.statusOffline}>
                              {user.is_online ? 'Online' : 'Offline'}
                            </span>
                          </div>
                        </td>
                        <td>
                          <span className={styles.dateText}>
                            {new Date(user.created_at).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </span>
                        </td>
                        <td>
                          <div className={styles.actionButtons}>
                            <button
                              className={styles.editBtn}
                              onClick={() => handleEdit(user)}
                              title="Edit user"
                            >
                              <span className="material-icons">edit</span>
                            </button>
                            {deleteConfirm === user.id ? (
                              <div className={styles.deleteConfirmGroup}>
                                <button
                                  className={styles.confirmDeleteBtn}
                                  onClick={() => handleDelete(user.id)}
                                  title="Confirm delete"
                                >
                                  <span className="material-icons">check</span>
                                </button>
                                <button
                                  className={styles.cancelDeleteBtn}
                                  onClick={() => setDeleteConfirm(null)}
                                  title="Cancel"
                                >
                                  <span className="material-icons">close</span>
                                </button>
                              </div>
                            ) : (
                              <button
                                className={styles.deleteBtn}
                                onClick={() => setDeleteConfirm(user.id)}
                                title="Delete user"
                              >
                                <span className="material-icons">delete_outline</span>
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className={styles.tableFooter}>
              <span className={styles.resultCount}>
                Showing {filteredUsers.length} of {totalUsers} users
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
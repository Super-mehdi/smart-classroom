import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import styles from './Layout.module.css';

const Layout = () => {
  const { currentUser, logout } = useAuth();
  const location = useLocation();

  const getPageTitle = (pathname) => {
    const path = pathname.split('/').filter(Boolean)[0] || 'home';
    return path.charAt(0).toUpperCase() + path.slice(1);
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const navLinks = {
    teacher: [
      { path: '/', label: 'Home', icon: 'home' },
      { path: '/sessions', label: 'Sessions', icon: 'video_library' },
      { path: '/students', label: 'Students', icon: 'people' },
    ],
    superuser: [
      { path: '/admin', label: 'Admin', icon: 'admin_panel_settings' },
    ],
  };

  const role = currentUser?.role?.toLowerCase() === 'superuser' ? 'superuser' : 'teacher';
  const links = navLinks[role];

  return (
    <div className={styles.container}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>SmartClass</div>
        <nav className={styles.nav}>
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.activeNavLink : ''}`
              }
            >
              <span className={`material-icons ${styles.navIcon}`}>{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <button onClick={logout} className={styles.logoutButton}>
          <span className={`material-icons ${styles.navIcon}`}>logout</span> Logout
        </button>
      </aside>

      <div className={styles.mainWrapper}>
        <header className={styles.topBar}>
          <h1 className={styles.pageTitle}>{getPageTitle(location.pathname)}</h1>
          <div className={styles.topBarRight}>
            <span className={`material-icons ${styles.bellIcon}`} title="Alerts">notifications</span>
            <div className={styles.avatar} title={currentUser?.name}>
              {getInitials(currentUser?.name)}
            </div>
          </div>
        </header>

        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;

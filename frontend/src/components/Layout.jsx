import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

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
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="fixed w-56 h-screen bg-white border-r border-gray-200 shadow-sm flex flex-col z-50">
        <div className="p-6 text-xl font-bold text-blue-600 flex items-center gap-2">
            🎓 SmartClass
        </div>
        <nav className="flex-1 px-2 space-y-1 mt-4">
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700'
                }`
              }
            >
              <span className="material-icons text-lg">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <button onClick={logout} className="px-6 py-4 text-red-500 hover:bg-red-50 flex items-center gap-3 font-medium text-sm">
          <span className="material-icons text-lg">logout</span> Logout
        </button>
      </aside>

      <div className="flex-1 ml-56 flex flex-col">
        <header className="h-16 bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center shadow-sm">
          <h1 className="text-lg font-medium text-gray-800">{getPageTitle(location.pathname)}</h1>
          <div className="flex items-center gap-4">
            <span className="material-icons text-gray-500 cursor-pointer">notifications</span>
            <div className="w-9 h-9 rounded-full bg-blue-600 text-white flex items-center justify-center font-medium text-sm">
              {getInitials(currentUser?.name)}
            </div>
          </div>
        </header>

        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;

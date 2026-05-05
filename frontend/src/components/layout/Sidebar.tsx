import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import SonarRing from '../SonarRing';
import { useAuthStore } from '../../stores/authStore';
import './Sidebar.css';

interface NavItem {
  path:  string;
  label: string;
  icon:  string;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard',  label: 'Dashboard',  icon: '◈' },
  { path: '/identify',   label: 'Identify',   icon: '⬡' },
  { path: '/turtles',    label: 'Catalog',    icon: '◉' },
  { path: '/encounters', label: 'Encounters', icon: '◎' },
];

/**
 * Application sidebar with navigation and user info.
 * Responsibility: display nav links and current user identity.
 */
const Sidebar: React.FC = () => {
  const { user, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <aside className="sidebar" aria-label="Main navigation">
      {/* Brand / Logo area */}
      <div className="sidebar__brand">
        <SonarRing size={48} rings={2} />
        <div className="sidebar__brand-text">
          <span className="sidebar__brand-name">SeaTurtle</span>
          <span className="sidebar__brand-sub">Photo-ID</span>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="sidebar__nav">
        <ul className="sidebar__nav-list" role="list">
          {NAV_ITEMS.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `sidebar__nav-item${isActive ? ' sidebar__nav-item--active' : ''}`
                }
              >
                <span className="sidebar__nav-icon" aria-hidden="true">{item.icon}</span>
                <span className="sidebar__nav-label">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* System status indicator */}
      <div className="sidebar__status">
        <span className="sidebar__status-dot" aria-hidden="true" />
        <span className="sidebar__status-text">System Online</span>
      </div>

      {/* User info + logout */}
      <div className="sidebar__user">
        <div className="sidebar__user-info">
          <span className="sidebar__user-name">{user?.fullName ?? 'Researcher'}</span>
          <span className="sidebar__user-role tag">{user?.role ?? ''}</span>
        </div>
        <button
          className="sidebar__logout"
          onClick={handleLogout}
          aria-label="Logout"
        >
          ⏻
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

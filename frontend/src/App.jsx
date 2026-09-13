import { useState } from 'react';
import { useAuth } from './auth/AuthContext.jsx';
import LoginPage from './auth/LoginPage.jsx';
import ProtectedRoute from './auth/ProtectedRoute.jsx';

import MobileSimulator from './components/MobileSimulator.jsx';
import AnalystDashboard from './components/AnalystDashboard.jsx';
import UserManagement from './components/UserManagement.jsx';
import AuditLogs from './components/AuditLogs.jsx';
import HealthMetrics from './components/HealthMetrics.jsx';

const TABS = [
  { id: 'mobile',     label: 'Mobile App',        roles: ['admin', 'analyst'] },
  { id: 'dashboard',  label: 'Analyst Dashboard', roles: ['admin', 'analyst'] },
  { id: 'users',      label: 'Users',             roles: ['admin'] },
  { id: 'audit',      label: 'Audit Logs',        roles: ['admin'] },
  { id: 'health',     label: 'Health',            roles: ['admin'] },
];

export default function App() {
  const { isAuthenticated, user, logout } = useAuth();
  const [activeView, setActiveView] = useState('mobile');

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const visibleTabs = TABS.filter((t) => t.roles.includes(user.role));

  return (
    <div>
      <div className="topbar">
        <div className="brand">
          <div className="oval">MTN</div>
          <div className="title">MoMo <span>Guard</span></div>
        </div>
        <div className="topbar-right">
          <span className="topbar-tag">
            {user.full_name || user.email} · <b>{user.role}</b>
          </span>
          <button className="logout-btn" onClick={logout}>Sign out</button>
        </div>
      </div>

      <div className="navbar">
        {visibleTabs.map((tab) => (
          <button
            key={tab.id}
            className={activeView === tab.id ? 'navbtn active' : 'navbtn'}
            onClick={() => setActiveView(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="wrap">
        {activeView === 'mobile' && (
          <ProtectedRoute>
            <MobileSimulator />
          </ProtectedRoute>
        )}

        {activeView === 'dashboard' && (
          <ProtectedRoute>
            <AnalystDashboard key="dashboard" />
          </ProtectedRoute>
        )}

        {activeView === 'users' && (
          <ProtectedRoute requireRole="admin">
            <UserManagement />
          </ProtectedRoute>
        )}

        {activeView === 'audit' && (
          <ProtectedRoute requireRole="admin">
            <AuditLogs />
          </ProtectedRoute>
        )}

        {activeView === 'health' && (
          <ProtectedRoute requireRole="admin">
            <HealthMetrics />
          </ProtectedRoute>
        )}
      </div>
    </div>
  );
}
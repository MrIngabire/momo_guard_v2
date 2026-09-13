import { useAuth } from './AuthContext.jsx';

export default function ProtectedRoute({ requireRole, children }) {
  const { loading, isAuthenticated, user } = useAuth();

  if (loading) {
    return <div className="panel" style={{ margin: 40 }}>Loading…</div>;
  }

  if (!isAuthenticated) {
    return null; // App.jsx will render LoginPage instead
  }

  if (requireRole && user.role !== requireRole) {
    return (
      <div className="panel" style={{ margin: 40 }}>
        <h3>Access denied</h3>
        <p style={{ color: 'var(--muted)' }}>
          This area requires the <b>{requireRole}</b> role. You are signed in as <b>{user.role}</b>.
        </p>
      </div>
    );
  }

  return children;
}
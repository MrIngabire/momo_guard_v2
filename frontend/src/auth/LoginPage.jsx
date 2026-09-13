import { useState } from 'react';
import { useAuth } from './AuthContext.jsx';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-brand">
          <div className="oval">MTN</div>
          <div className="title">MoMo <span>Guard</span></div>
        </div>
        <h1>Analyst Console</h1>
        <p className="sub">Sign in to access the threat dashboard.</p>

        <form onSubmit={handleSubmit} className="login-form">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@momoguard.rw"
            autoComplete="username"
            required
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />

          <button type="submit" className="action-btn primary" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

          {error && <p className="login-error">{error}</p>}
        </form>

        <div className="login-hint">
          <strong>Demo credentials</strong>
          <div>admin@momoguard.rw / Admin@1234</div>
          <div>analyst@momoguard.rw / Analyst@1234</div>
        </div>
      </div>
    </div>
  );
}
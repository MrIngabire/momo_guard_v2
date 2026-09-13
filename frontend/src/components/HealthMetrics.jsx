import { useEffect, useState } from 'react';
import { api } from '../apiClient';

export default function HealthMetrics() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const [retraining, setRetraining] = useState(false);
  const [message, setMessage] = useState(null);

  const refresh = async () => {
    setError(null);
    try {
      const res = await api.get('/api/health');
      setHealth(res);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => { refresh(); }, []);

  const triggerRetrain = async () => {
    setRetraining(true);
    setMessage(null);
    try {
      const res = await api.post('/api/retrain');
      setMessage(`Retrained. Accuracy: ${(res.accuracy * 100).toFixed(1)}% (${res.samples} samples)`);
      await refresh();
    } catch (err) {
      setMessage(`Retrain failed: ${err.message}`);
    } finally {
      setRetraining(false);
    }
  };

  return (
    <div>
      <div className="panel" style={{ marginBottom: 20 }}>
        <div className="panel-head">
          <h3>System health</h3>
          <div className="sub">Live status and metrics</div>
          <button className="navbtn" style={{ marginLeft: 'auto' }} onClick={refresh}>↻ Refresh</button>
        </div>

        {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

        {health && (
          <div className="stat-grid">
            <div className="stat-card accent">
              <div className="k">Status</div>
              <div className="v">{health.status}</div>
            </div>
            <div className="stat-card">
              <div className="k">Total scans</div>
              <div className="v">{health.scans}</div>
            </div>
            <div className="stat-card">
              <div className="k">Users</div>
              <div className="v">{health.users}</div>
            </div>
            <div className="stat-card">
              <div className="k">Model</div>
              <div className="v" style={{ fontSize: 18 }}>{health.metrics.model || '—'}</div>
            </div>
          </div>
        )}
      </div>

      <div className="panel">
        <div className="panel-head">
          <h3>ML model</h3>
          <div className="sub">Retrain on the bundled corpus</div>
        </div>

        {health?.metrics && (
          <ul style={{ lineHeight: 1.8, color: 'var(--muted)' }}>
            <li><b>Model:</b> {health.metrics.model}</li>
            <li><b>Samples:</b> {health.metrics.samples}</li>
            <li><b>CV folds:</b> {health.metrics.cv_folds}</li>
            <li>
              <b>CV accuracy:</b>{' '}
              {health.metrics.accuracy != null
                ? `${(health.metrics.accuracy * 100).toFixed(2)}% ± ${(health.metrics.accuracy_std * 100).toFixed(2)}%`
                : '—'}
            </li>
          </ul>
        )}

        <button className="action-btn primary" onClick={triggerRetrain} disabled={retraining}>
          {retraining ? 'Retraining…' : 'Trigger retrain'}
        </button>

        {message && <p style={{ marginTop: 12, color: 'var(--muted)' }}>{message}</p>}
      </div>
    </div>
  );
}
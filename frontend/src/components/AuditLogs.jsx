import { useEffect, useState } from 'react';
import { api } from '../apiClient';

const formatDate = (iso) => {
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
};

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/audit-logs?limit=200');
      setLogs(res.logs);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  return (
    <div className="panel">
      <div className="panel-head">
        <h3>Audit logs</h3>
        <div className="sub">Every privileged action, newest first</div>
        <button className="navbtn" style={{ marginLeft: 'auto' }} onClick={refresh}>↻ Refresh</button>
      </div>

      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading && !logs.length && <p>Loading…</p>}

      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Actor</th>
            <th>Action</th>
            <th>Target</th>
            <th>Detail</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.log_id}>
              <td>{formatDate(l.timestamp)}</td>
              <td className="mono">{l.actor_email || '—'}</td>
              <td><span className="lang-chip">{l.action}</span></td>
              <td className="mono">{l.target || '—'}</td>
              <td className="msg-cell">{l.detail || '—'}</td>
              <td className="mono">{l.ip_address || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
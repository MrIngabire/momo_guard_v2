import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { api } from '../apiClient';

const scoreClass = (score) => {
  if (score >= 0.75) return 'score-pill high';
  if (score >= 0.5) return 'score-pill mid';
  return 'score-pill low';
};

const formatDate = (iso) => {
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
};

export default function AnalystDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dash, scansRes] = await Promise.all([
        api.get('/api/dashboard'),
        api.get('/api/scans'),
      ]);
      setDashboard(dash);
      setScans(scansRes.scans);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  if (loading && !dashboard) return <div className="panel">Loading dashboard…</div>;
  if (error && !dashboard) return <div className="panel">Error: {error}</div>;
  if (!dashboard) return null;

  const chartData = dashboard.recent_flagged.map((s) => ({
    name: s.sender_id.length > 10 ? s.sender_id.slice(0, 10) + '…' : s.sender_id,
    ThreatScore: Math.round(s.fraud_score * 100),
  }));

  const accuracyPct = dashboard.model_accuracy != null
    ? `${(dashboard.model_accuracy * 100).toFixed(1)}%`
    : '—';

  return (
    <div>
      <div className="panel" style={{ marginBottom: 24, display: 'flex', gap: 12, alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>Threat Overview</h3>
        <button className="navbtn" style={{ marginLeft: 'auto' }} onClick={refresh}>
          ↻ Refresh
        </button>
      </div>

      <div className="stat-grid">
        <div className="stat-card accent">
          <div className="k">Messages scanned</div>
          <div className="v">{dashboard.total_scans}</div>
        </div>
        <div className="stat-card">
          <div className="k">Smishing blocked</div>
          <div className="v">{dashboard.total_blocked}</div>
        </div>
        <div className="stat-card">
          <div className="k">Suspicious</div>
          <div className="v">{dashboard.total_suspicious}</div>
        </div>
        <div className="stat-card">
          <div className="k">Model accuracy (CV)</div>
          <div className="v">{accuracyPct}</div>
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 20 }}>
        <div className="panel-head">
          <h3>Recent threat scores</h3>
          <div className="sub">Probability of fraud on recent flagged messages</div>
        </div>
        <div style={{ width: '100%', height: 300, minHeight: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E7E3D8" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B6B63' }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B6B63' }} domain={[0, 100]} />
              <Tooltip cursor={{ fill: '#FDEAEC' }} />
              <Bar dataKey="ThreatScore" fill="#D6273C" radius={[4, 4, 0, 0]} maxBarSize={50} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="dash-grid">
        <div className="panel">
          <div className="panel-head">
            <h3>Recent classifications</h3>
            <div className="sub">Most recent flagged scans</div>
          </div>
          <table>
            <thead>
              <tr>
                <th>Sender</th>
                <th>Message</th>
                <th>Tag</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {dashboard.recent_flagged.map((s) => (
                <tr key={s.scan_id}>
                  <td className="mono">{s.sender_id}</td>
                  <td className="msg-cell">{s.text_body.slice(0, 60)}…</td>
                  <td><span className="lang-chip">{s.classification}</span></td>
                  <td><span className={scoreClass(s.fraud_score)}>{Math.round(s.fraud_score * 100)}%</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="panel">
          <div className="panel-head">
            <h3>Blacklisted senders</h3>
            <div className="sub">Auto-updated from feedback</div>
          </div>
          {dashboard.blacklisted_senders.length === 0 ? (
            <p>No blacklisted senders yet.</p>
          ) : (
            dashboard.blacklisted_senders.map((b) => (
              <div className="bl-item" key={b.blacklist_id}>
                <div>
                  <div className="bl-num">{b.phone_number}</div>
                  <div className="bl-count">Reported {b.report_count} times</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="panel" style={{ marginTop: 20 }}>
        <div className="panel-head">
          <h3>All scans</h3>
          <div className="sub">Full history</div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Sender</th>
              <th>Message</th>
              <th>Tag</th>
              <th>Score</th>
              <th>Engine</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((s) => (
              <tr key={s.scan_id}>
                <td className="mono">{s.sender_id}</td>
                <td className="msg-cell">{s.text_body.slice(0, 60)}…</td>
                <td><span className="lang-chip">{s.classification}</span></td>
                <td><span className={scoreClass(s.fraud_score)}>{Math.round(s.fraud_score * 100)}%</span></td>
                <td><span className="lang-chip">{s.engine || '—'}</span></td>
                <td>{formatDate(s.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
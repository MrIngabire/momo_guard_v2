import { useEffect, useState } from 'react';
import { api } from '../apiClient';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/users');
      setUsers(res.users);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  const updateUser = async (user_id, patch) => {
    try {
      await api.patch(`/api/users/${user_id}`, patch);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteUser = async (user_id, email) => {
    if (!window.confirm(`Delete user ${email}? This cannot be undone.`)) return;
    try {
      await api.delete(`/api/users/${user_id}`);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="panel">
      <div className="panel-head">
        <h3>User management</h3>
        <div className="sub">Roles and access control</div>
      </div>

      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
      {loading && !users.length && <p>Loading…</p>}

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.user_id}>
              <td>{u.full_name || '—'}</td>
              <td className="mono">{u.email}</td>
              <td>
                <select
                  value={u.role}
                  onChange={(e) => updateUser(u.user_id, { role: e.target.value })}
                  style={{ padding: 4, borderRadius: 6 }}
                >
                  <option value="analyst">analyst</option>
                  <option value="admin">admin</option>
                </select>
              </td>
              <td>
                <span className={u.is_active ? 'score-pill low' : 'score-pill high'}>
                  {u.is_active ? 'active' : 'disabled'}
                </span>
              </td>
              <td>{new Date(u.created_at).toLocaleDateString()}</td>
              <td>
                <button
                  className="row-action"
                  style={{ marginRight: 6 }}
                  onClick={() => updateUser(u.user_id, { is_active: !u.is_active })}
                >
                  {u.is_active ? 'Disable' : 'Enable'}
                </button>
                <button className="row-action" onClick={() => deleteUser(u.user_id, u.email)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
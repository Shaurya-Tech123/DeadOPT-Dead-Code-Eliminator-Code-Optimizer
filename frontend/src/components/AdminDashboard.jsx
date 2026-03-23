import { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = ({ onBack }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/admin/logs?limit=100');
      if (response.data.success) {
        setLogs(response.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-dark-bg p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={onBack}
            className="px-4 py-2 bg-dark-card hover:bg-dark-surface rounded-lg transition-colors"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-accent">Admin Dashboard</h1>
          <button
            onClick={fetchLogs}
            className="px-4 py-2 bg-accent text-dark-bg hover:bg-accent-hover rounded-lg transition-colors font-semibold"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-dark-card p-4 rounded-lg">
            <div className="text-gray-400 text-sm">Total Optimizations</div>
            <div className="text-2xl font-bold text-accent">{logs.length}</div>
          </div>
          <div className="bg-dark-card p-4 rounded-lg">
            <div className="text-gray-400 text-sm">Python</div>
            <div className="text-2xl font-bold text-accent">
              {logs.filter(l => l.language === 'python').length}
            </div>
          </div>
          <div className="bg-dark-card p-4 rounded-lg">
            <div className="text-gray-400 text-sm">C/C++</div>
            <div className="text-2xl font-bold text-accent">
              {logs.filter(l => l.language === 'c' || l.language === 'cpp').length}
            </div>
          </div>
          <div className="bg-dark-card p-4 rounded-lg">
            <div className="text-gray-400 text-sm">Java</div>
            <div className="text-2xl font-bold text-accent">
              {logs.filter(l => l.language === 'java').length}
            </div>
          </div>
        </div>

        {/* Logs Table */}
        <div className="bg-dark-card rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-accent">Optimization Logs</h2>
          
          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading logs...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-400">{error}</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-gray-400">No logs found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-accent/30">
                    <th className="text-left p-3 text-gray-300">Timestamp</th>
                    <th className="text-left p-3 text-gray-300">Language</th>
                    <th className="text-left p-3 text-gray-300">Lines Removed</th>
                    <th className="text-left p-3 text-gray-300">IP Address</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log._id} className="border-b border-dark-surface hover:bg-dark-surface transition-colors">
                      <td className="p-3 text-gray-400 text-sm">{formatDate(log.timestamp)}</td>
                      <td className="p-3">
                        <span className="px-2 py-1 bg-accent/20 text-accent rounded text-sm font-semibold">
                          {log.language.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-3 text-accent font-semibold">{log.linesRemoved}</td>
                      <td className="p-3 text-gray-400 text-sm">{log.ipAddress || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
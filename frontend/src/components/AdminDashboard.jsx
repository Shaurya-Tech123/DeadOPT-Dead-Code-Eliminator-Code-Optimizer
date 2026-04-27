import { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = ({ onBack, onOpenItem }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/history?limit=100');
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

  const downloadCode = (code, language, kind = 'optimized') => {
    const blob = new Blob([code || ''], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    let ext = '.txt';
    if (language === 'c') ext = '.c';
    if (language === 'cpp') ext = '.cpp';
    if (language === 'java') ext = '.java';
    if (language === 'python') ext = '.py';

    link.setAttribute('download', `${kind}_code${ext}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const deleteItem = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/history/${id}`);
      await fetchLogs();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to delete history item');
    }
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

        {/* History Cards */}
        <div className="bg-dark-card rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-accent">Optimization History</h2>
          
          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading logs...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-400">{error}</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-gray-400">No logs found</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {logs.map((log) => (
                <div key={log._id} className="bg-dark-surface rounded-lg p-4 border border-accent/10">
                  <div className="flex justify-between items-center mb-3">
                    <span className="px-2 py-1 bg-accent/20 text-accent rounded text-sm font-semibold">
                      {(log.language || 'unknown').toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-400">{formatDate(log.createdAt || log.timestamp)}</span>
                  </div>
                  <div className="text-sm text-gray-300 mb-4">
                    Lines Removed: <span className="text-accent font-semibold">{log.linesRemoved || 0}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => onOpenItem?.(log)}
                      className="px-3 py-2 bg-accent text-dark-bg rounded hover:bg-accent-hover font-semibold"
                    >
                      Open
                    </button>
                    <button
                      onClick={() => downloadCode(log.optimizedCode, log.language, 'optimized')}
                      className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 font-semibold"
                    >
                      Download
                    </button>
                    <button
                      onClick={() => deleteItem(log._id)}
                      className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-semibold"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
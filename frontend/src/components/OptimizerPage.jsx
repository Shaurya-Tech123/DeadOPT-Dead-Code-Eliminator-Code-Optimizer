import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const OptimizerPage = ({ initialResult, onBack, onAdmin }) => {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(initialResult || null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const languageConfig = {
    python: { label: 'Python', extension: '.py', monacoLang: 'python' },
    c: { label: 'C', extension: '.c', monacoLang: 'c' },
    cpp: { label: 'C++', extension: '.cpp', monacoLang: 'cpp' },
    java: { label: 'Java', extension: '.java', monacoLang: 'java' },
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setCode(event.target.result);
      // Detect language from extension
      const ext = file.name.split('.').pop().toLowerCase();
      const langMap = {
        'c': 'c',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'java': 'java',
        'py': 'python'
      };
      if (langMap[ext]) {
        setLanguage(langMap[ext]);
      }
    };
    reader.readAsText(file);
  };

  const handleOptimize = async () => {
    if (!code.trim()) {
      setError('Please enter some code to optimize');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5000/api/optimize', {
        code,
        language
      });

      if (response.data.success) {
        setResult(response.data);
      } else {
        setError(response.data.error || 'Optimization failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to optimize code');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result?.optimizedCode) return;

    const blob = new Blob([result.optimizedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `optimized${languageConfig[language].extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-dark-bg p-4 md:p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex justify-between items-center mb-4">
          <button
            onClick={onBack}
            className="px-4 py-2 bg-dark-card hover:bg-dark-surface rounded-lg transition-colors"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-accent">DeadOPT Optimizer</h1>
          <button
            onClick={onAdmin}
            className="px-4 py-2 bg-dark-card hover:bg-dark-surface rounded-lg transition-colors"
          >
            Admin
          </button>
        </div>

        {/* Language Selector */}
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.entries(languageConfig).map(([key, config]) => (
            <button
              key={key}
              onClick={() => setLanguage(key)}
              className={`px-4 py-2 rounded-lg transition-all ${
                language === key
                  ? 'bg-accent text-dark-bg font-semibold'
                  : 'bg-dark-card hover:bg-dark-surface'
              }`}
            >
              {config.label}
            </button>
          ))}
        </div>

        {/* File Upload */}
        <div className="mb-4">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".c,.cpp,.cc,.cxx,.java,.py"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 bg-dark-card hover:bg-dark-surface rounded-lg transition-colors"
          >
            📁 Upload File
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Code Editor */}
        <div className="bg-dark-card rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4 text-accent">Original Code</h2>
          <div className="border border-accent/30 rounded-lg overflow-hidden" style={{ height: '500px' }}>
            <Editor
              height="100%"
              language={languageConfig[language].monacoLang}
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                wordWrap: 'on',
                scrollBeyondLastLine: false,
              }}
            />
          </div>
          <button
            onClick={handleOptimize}
            disabled={loading || !code.trim()}
            className="mt-4 w-full px-6 py-3 bg-accent text-dark-bg font-semibold rounded-lg hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? 'Optimizing...' : '🚀 Optimize Code'}
          </button>
        </div>

        {/* Results */}
        <div className="bg-dark-card rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4 text-accent">Optimized Code</h2>
          {error && (
            <div className="mb-4 p-4 bg-red-900/30 border border-red-500 rounded-lg text-red-300">
              {error}
            </div>
          )}
          {result ? (
            <>
              <div className="border border-accent/30 rounded-lg overflow-hidden mb-4" style={{ height: '500px' }}>
                <Editor
                  height="100%"
                  language={languageConfig[language].monacoLang}
                  value={result.optimizedCode}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    wordWrap: 'on',
                    scrollBeyondLastLine: false,
                    readOnly: true,
                  }}
                />
              </div>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between items-center p-3 bg-dark-surface rounded-lg">
                  <span className="text-gray-300">Lines Removed:</span>
                  <span className="text-accent font-semibold">{result.linesRemoved}</span>
                </div>
                <button
                  onClick={handleDownload}
                  className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all"
                >
                  📥 Download Optimized Code
                </button>
              </div>
            </>
          ) : (
            <div className="border border-accent/30 rounded-lg h-[500px] flex items-center justify-center text-gray-400">
              {loading ? 'Optimizing your code...' : 'Optimized code will appear here'}
            </div>
          )}
        </div>
      </div>

      {/* Optimization Report */}
      {result?.report && (
        <div className="max-w-7xl mx-auto mt-6 bg-dark-card rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-accent">Optimization Report</h2>
          <pre className="bg-dark-surface p-4 rounded-lg overflow-x-auto text-sm">
            {JSON.stringify(result.report, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default OptimizerPage;
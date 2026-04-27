import { useEffect, useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const OptimizerPage = ({ initialSession, onBack, onAdmin }) => {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  useEffect(() => {
    if (!initialSession) return;
    if (initialSession.language) setLanguage(initialSession.language);
    if (typeof initialSession.code === 'string') setCode(initialSession.code);
    if (initialSession.result) setResult(initialSession.result);
  }, [initialSession]);


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

      {result && (
        <div className="max-w-7xl mx-auto mt-6 space-y-6">
          <div className="bg-dark-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-accent">Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-dark-surface rounded-lg p-4">
                <p className="text-sm text-gray-400">Language</p>
                <p className="text-lg font-semibold">{result.report?.summary?.language || language}</p>
              </div>
              <div className="bg-dark-surface rounded-lg p-4">
                <p className="text-sm text-gray-400">Lines Removed</p>
                <p className="text-lg font-semibold text-accent">{result.report?.summary?.linesRemoved ?? result.linesRemoved}</p>
              </div>
              <div className="bg-dark-surface rounded-lg p-4">
                <p className="text-sm text-gray-400">Improvement</p>
                <p className="text-lg font-semibold text-green-400">{result.report?.summary?.improvementPercent ?? 0}%</p>
              </div>
            </div>
          </div>

          <div className="bg-dark-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-accent">Optimizations Applied</h2>
            <ul className="list-disc pl-6 space-y-1 text-gray-200">
              {(result.report?.optimizationsApplied || []).map((opt, idx) => (
                <li key={`${opt}-${idx}`}>{opt}</li>
              ))}
            </ul>
          </div>

          <div className="bg-dark-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-accent">Before vs After</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold mb-2 text-gray-300">Before</h3>
                <pre className="bg-dark-surface p-4 rounded-lg overflow-auto max-h-72 text-sm">{result.report?.beforeAfter?.before || code}</pre>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-gray-300">After</h3>
                <pre className="bg-dark-surface p-4 rounded-lg overflow-auto max-h-72 text-sm">{result.report?.beforeAfter?.after || result.optimizedCode}</pre>
              </div>
            </div>
          </div>

          <div className="bg-dark-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-accent">Complexity Impact</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-dark-surface rounded-lg p-4">
                <p className="text-sm text-gray-400">Before</p>
                <p className="text-lg font-semibold">{result.report?.complexityImpact?.before ?? '-'}</p>
              </div>
              <div className="bg-dark-surface rounded-lg p-4">
                <p className="text-sm text-gray-400">After</p>
                <p className="text-lg font-semibold">{result.report?.complexityImpact?.after ?? '-'}</p>
              </div>
              <div className="bg-dark-surface rounded-lg p-4">
                <p className="text-sm text-gray-400">Delta</p>
                <p className="text-lg font-semibold text-green-400">{result.report?.complexityImpact?.delta ?? '-'}</p>
              </div>
            </div>
          </div>

          <div className="bg-dark-card rounded-lg p-6 overflow-auto">
            <h2 className="text-xl font-semibold mb-4 text-accent">Symbol Table</h2>
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-dark-surface">
                  <th className="py-2">Variable Name</th>
                  <th className="py-2">Type</th>
                  <th className="py-2">Scope</th>
                  <th className="py-2">Line Declared</th>
                  <th className="py-2">Usage Count</th>
                </tr>
              </thead>
              <tbody>
                {(result.symbolTable || []).map((row, idx) => (
                  <tr key={`${row.name}-${idx}`} className="border-b border-dark-surface/40">
                    <td className="py-2">{row.name}</td>
                    <td className="py-2">{row.type}</td>
                    <td className="py-2">{row.scope}</td>
                    <td className="py-2">{row.lineDeclared}</td>
                    <td className="py-2">{row.usageCount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={handleDownload}
              className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all"
            >
              📥 Download Optimized Code
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizerPage;
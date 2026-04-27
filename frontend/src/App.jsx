import './App.css';

import { useState } from 'react';

import AdminDashboard from './components/AdminDashboard';
import LandingPage from './components/LandingPage';
import OptimizerPage from './components/OptimizerPage';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [optimizerSession, setOptimizerSession] = useState(null);

  const handleOptimize = (result) => {
    setOptimizerSession(result);
    setCurrentPage('optimizer');
  };

  const handleOpenHistoryItem = (item) => {
    setOptimizerSession({
      code: item.originalCode || '',
      language: item.language || 'python',
      result: {
        optimizedCode: item.optimizedCode || '',
        report: item.report || {},
        symbolTable: item.symbolTable || [],
        linesRemoved: item.linesRemoved || 0,
      },
    });
    setCurrentPage('optimizer');
  };

  return (
    <div className="App">
      {currentPage === 'landing' && (
        <LandingPage 
          onGetStarted={() => setCurrentPage('optimizer')}
          onOptimize={handleOptimize}
        />
      )}
      {currentPage === 'optimizer' && (
        <OptimizerPage 
          initialSession={optimizerSession}
          onBack={() => setCurrentPage('landing')}
          onAdmin={() => setCurrentPage('Dashboard')}
        />
      )}
      {currentPage === 'Dashboard' && (
        <AdminDashboard
          onBack={() => setCurrentPage('optimizer')}
          onOpenItem={handleOpenHistoryItem}
        />
      )}
    </div>
  );
}

export default App;
import { useState } from 'react';
import LandingPage from './components/LandingPage';
import OptimizerPage from './components/OptimizerPage';
import AdminDashboard from './components/AdminDashboard';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [optimizationResult, setOptimizationResult] = useState(null);

  const handleOptimize = (result) => {
    setOptimizationResult(result);
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
          initialResult={optimizationResult}
          onBack={() => setCurrentPage('landing')}
          onAdmin={() => setCurrentPage('admin')}
        />
      )}
      {currentPage === 'admin' && (
        <AdminDashboard onBack={() => setCurrentPage('optimizer')} />
      )}
    </div>
  );
}

export default App;
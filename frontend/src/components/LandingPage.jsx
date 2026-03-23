import { useState } from 'react';

const LandingPage = ({ onGetStarted, onOptimize }) => {
  const handleGetStarted = () => {
    onGetStarted();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden animate-fade-in">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-accent rounded-full animate-pulse-slow"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      {/* Main content */}
      <div className="z-10 text-center px-4 animate-slide-up">
        <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-accent to-blue-400 bg-clip-text text-transparent">
          DeadOPT
        </h1>

        <p className="text-xl md:text-2xl text-gray-300 mb-4">
          Multi-Language Dead Code Optimizer
        </p>

        <p className="text-gray-400 mb-12 max-w-2xl mx-auto">
          Analyze and remove dead code from C, C++, Java, and Python projects.
          Optimize your codebase with intelligent static analysis.
        </p>

        <div className="flex flex-wrap justify-center gap-4">
          <button
            onClick={handleGetStarted}
            className="px-8 py-4 bg-accent text-dark-bg font-semibold rounded-lg hover:bg-accent-hover transition-all duration-300 transform hover:scale-105 shadow-lg shadow-accent/50"
          >
            Get Started
          </button>
        </div>

        {/* Language badges */}
        <div className="mt-16 flex flex-wrap justify-center gap-4">
          {['C', 'C++', 'Java', 'Python'].map((lang, idx) => (
            <div
              key={lang}
              className="px-6 py-3 bg-dark-card rounded-lg border border-accent/30 hover:border-accent transition-all"
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              <span className="text-accent font-semibold">{lang}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
        <div className="w-6 h-10 border-2 border-accent rounded-full flex justify-center">
          <div className="w-1 h-3 bg-accent rounded-full mt-2 animate-bounce" />
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
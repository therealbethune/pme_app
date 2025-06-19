import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './layout/Sidebar';
import Header from './layout/Header';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Analysis from './pages/Analysis';
import Portfolio from './pages/Portfolio';
import Settings from './pages/Settings';
import './styles/global.css';

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <Router>
      <div className={isDarkMode ? 'dark' : ''}>
        <Sidebar>
          <Header 
            isDark={isDarkMode} 
            onToggleDarkMode={toggleDarkMode} 
          />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </Sidebar>
      </div>
    </Router>
  );
};

export default App; 
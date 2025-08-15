/**
 * File: App.tsx
 * 
 * Overview:
 * Main application component with routing configuration
 * 
 * Purpose:
 * Provides the main application structure and route definitions
 * 
 * Dependencies:
 * - React Router DOM for routing
 * - Layout components
 * - Page components
 * 
 * Last Modified: 2025-08-15
 * Author: Claude
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './layouts/Layout';
import HomePage from './pages/HomePage';
import ImportPage from './pages/ImportPage';
import AnalysisPage from './pages/AnalysisPage';
import ResultsPage from './pages/ResultsPage';
import NotFoundPage from './pages/NotFoundPage';

const App: React.FC = () => {
  return (
    <div className="App">
      <Routes>
        {/* Main application routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="import" element={<ImportPage />} />
          <Route path="analysis" element={<AnalysisPage />} />
          <Route path="results" element={<ResultsPage />} />
          <Route path="results/:jobId" element={<ResultsPage />} />
        </Route>
        
        {/* 404 page */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  );
};

export default App;
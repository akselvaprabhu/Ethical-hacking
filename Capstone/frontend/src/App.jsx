import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import TrafficLogs from './pages/TrafficLogs';
import SecurityEvents from './pages/SecurityEvents';
import BlockedIps from './pages/BlockedIps';
import Login from './pages/Login';

// Protected Route Component requiring JWT token
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('jwt_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setRefreshTrigger(prev => prev + 1);
    setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <Router>
      <div className="min-h-screen bg-[#0a0d14] text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
        <Navbar onRefresh={handleRefresh} isRefreshing={isRefreshing} />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Dashboard triggerRefresh={refreshTrigger} />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/logs" 
              element={
                <ProtectedRoute>
                  <TrafficLogs />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/events" 
              element={
                <ProtectedRoute>
                  <SecurityEvents />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/blocked" 
              element={
                <ProtectedRoute>
                  <BlockedIps />
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <footer className="border-t border-slate-800/80 py-4 bg-[#0c1017]">
          <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500 flex flex-col sm:flex-row justify-between items-center gap-2">
            <div>
              Academic Cyber Security Demonstration &bull; <strong className="text-slate-400">Intelligent API Protection Framework</strong>
            </div>
            <div className="font-mono text-[11px] text-slate-400">
              Signature Rules + Isolation Forest Anomaly Detection
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Shield, Activity, AlertTriangle, Lock, FileText, LogOut, RefreshCw, Trash2 } from 'lucide-react';
import { resetSecurityData } from '../services/api';

export default function Navbar({ onRefresh, isRefreshing }) {
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  const [isResetting, setIsResetting] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleReset = async () => {
    if (window.confirm("Are you sure you want to reset all traffic logs, security events, and active blocked IPs back to ZERO?")) {
      setIsResetting(true);
      try {
        await resetSecurityData();
        onRefresh();
      } catch (err) {
        console.error(err);
      } finally {
        setIsResetting(false);
      }
    }
  };

  const navItems = [
    { path: '/', label: 'SOC Overview', icon: Activity },
    { path: '/events', label: 'Security Threats', icon: AlertTriangle },
    { path: '/blocked', label: 'Active Firewall', icon: Lock },
    { path: '/logs', label: 'Traffic Logs', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#0c1017]/90 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo Brand */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-[#00f0ff]/10 rounded-lg border border-[#00f0ff]/30 text-[#00f0ff] glow-blue">
              <Shield className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wider text-slate-100 uppercase flex items-center gap-2">
                API Defender <span className="text-xs px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded font-mono">SOC v2.6</span>
              </h1>
              <p className="text-xs text-slate-400">Intelligent Runtime Protection Framework</p>
            </div>
          </div>

          {/* Nav Links - ONLY VISIBLE WHEN LOGGED IN */}
          {token ? (
            <nav className="hidden md:flex space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          ) : (
            <div className="hidden md:flex items-center gap-2 text-xs text-slate-500 font-mono">
              <Lock className="h-3.5 w-3.5 text-amber-400" />
              <span>Authentication Required to Access Dashboard</span>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center space-x-3">
            {token && (
              <>
                <button
                  onClick={onRefresh}
                  className={`p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium border border-slate-700 transition flex items-center gap-1.5 ${isRefreshing ? 'animate-spin text-[#00f0ff]' : ''}`}
                  title="Manual Telemetry Refresh"
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
                <button
                  onClick={handleReset}
                  disabled={isResetting}
                  className="px-2.5 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                  title="Reset All Telemetry & Logs to Zero"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  <span>Reset All to Zero</span>
                </button>
              </>
            )}

            {token ? (
              <button
                onClick={handleLogout}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30 rounded-lg text-xs font-semibold transition"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Logout</span>
              </button>
            ) : (
              <Link
                to="/login"
                className="px-3 py-1.5 bg-[#00f0ff]/10 text-[#00f0ff] hover:bg-[#00f0ff]/20 border border-[#00f0ff]/30 rounded-lg text-xs font-semibold transition"
              >
                Admin Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

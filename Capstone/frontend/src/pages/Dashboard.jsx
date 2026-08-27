import React, { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import TrafficChart from '../components/TrafficChart';
import AttackDistributionChart from '../components/AttackDistributionChart';
import EventTable from '../components/EventTable';
import BlockedIpTable from '../components/BlockedIpTable';
import { fetchSecurityStats, fetchTrafficChart, fetchSecurityEvents, fetchBlockedIps, unblockIpAddress } from '../services/api';
import { Activity, ShieldCheck, AlertTriangle, ShieldAlert, Lock, Cpu, Server } from 'lucide-react';

export default function Dashboard({ triggerRefresh }) {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [events, setEvents] = useState([]);
  const [blockedIps, setBlockedIps] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [sRes, cRes, eRes, bRes] = await Promise.all([
        fetchSecurityStats(),
        fetchTrafficChart(),
        fetchSecurityEvents(),
        fetchBlockedIps()
      ]);

      if (sRes.success) setStats(sRes);
      if (cRes.success) setChartData(cRes.chart_data);
      if (eRes.success) setEvents(eRes.events.slice(0, 10)); // Top 10 recent
      if (bRes.success) setBlockedIps(bRes.blocked_ips.filter(b => b.is_active));
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Poll every 3 seconds for real-time demonstration
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [triggerRefresh]);

  const handleUnblock = async (ip) => {
    await unblockIpAddress(ip);
    loadData();
  };

  if (loading && !stats) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <Activity className="h-8 w-8 text-[#00f0ff] animate-spin" />
        <p className="text-sm font-mono text-slate-400">Loading Intelligent SOC Security Dashboard...</p>
      </div>
    );
  }

  const overview = stats?.overview || {};

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-2xl border-l-4 border-l-[#00f0ff] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#00f0ff] uppercase tracking-wider mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Real-Time Engine Active
          </div>
          <h2 className="text-2xl font-extrabold text-slate-100">API Security & Attack Protection Center</h2>
          <p className="text-xs text-slate-400 mt-1">Dual-Engine Detection: Rule Signatures + Scikit-Learn Isolation Forest Anomaly Engine</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-2 bg-slate-900/80 rounded-lg border border-slate-800 text-xs font-mono flex items-center gap-2">
            <Cpu className="h-4 w-4 text-purple-400" />
            <span>ML Model: <strong className="text-purple-300">IsolationForest (v1.5)</strong></span>
          </div>
          <div className="px-3 py-2 bg-slate-900/80 rounded-lg border border-slate-800 text-xs font-mono flex items-center gap-2">
            <Server className="h-4 w-4 text-[#00f0ff]" />
            <span>Auto-Refresh: <strong className="text-[#00f0ff]">3s Live</strong></span>
          </div>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard title="Total Requests" value={overview.total_requests || 0} icon={Activity} color="blue" subtitle="Captured API requests" />
        <StatCard title="Normal Requests" value={overview.normal_requests || 0} icon={ShieldCheck} color="green" subtitle="Clean traffic allowed" />
        <StatCard title="Suspicious Traffic" value={overview.suspicious_requests || 0} icon={AlertTriangle} color="yellow" subtitle="Elevated risk score" />
        <StatCard title="Blocked Requests" value={overview.blocked_requests || 0} icon={ShieldAlert} color="red" subtitle="Runtime protection dropped" />
        <StatCard title="Active Blocked IPs" value={overview.active_threats || 0} icon={Lock} color="purple" subtitle="Active firewall bans" />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Real-time Traffic Time Series */}
        <div className="glass-panel p-5 rounded-2xl lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Activity className="h-4 w-4 text-[#00f0ff]" /> API Request Volume Telemetry
            </h3>
            <span className="text-xs text-slate-400 font-mono">5-minute sliding slots</span>
          </div>
          <TrafficChart data={chartData} />
        </div>

        {/* Attack Category Breakdown */}
        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-rose-400" /> Attack Type Distribution
            </h3>
            <span className="text-xs text-slate-400 font-mono">Detections</span>
          </div>
          <AttackDistributionChart data={stats?.attack_distribution || []} />
        </div>

      </div>

      {/* Bottom Grid: Recent Security Events & Active Blocked IPs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recent Security Threats Table */}
        <div className="glass-panel rounded-2xl lg:col-span-2 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" /> Recent Security Incidents
            </h3>
            <span className="text-xs text-slate-400 font-mono">Live feed</span>
          </div>
          <EventTable events={events} />
        </div>

        {/* Active Firewall Bans Table */}
        <div className="glass-panel rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Lock className="h-4 w-4 text-rose-400" /> Active Blocked IP List
            </h3>
            <span className="text-xs text-slate-400 font-mono">{blockedIps.length} Active</span>
          </div>
          <BlockedIpTable blockedIps={blockedIps} onUnblock={handleUnblock} />
        </div>

      </div>

    </div>
  );
}

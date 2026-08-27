import React, { useEffect, useState } from 'react';
import { fetchTrafficLogs } from '../services/api';
import { FileText, ChevronLeft, ChevronRight, Search } from 'lucide-react';

export default function TrafficLogs() {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const loadLogs = async (p = 1) => {
    setLoading(true);
    try {
      const res = await fetchTrafficLogs(p);
      if (res.success) {
        setLogs(res.logs);
        setTotalPages(res.pages);
        setPage(res.current_page);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs(page);
  }, [page]);

  const filteredLogs = logs.filter(l => 
    l.ip_address.includes(searchTerm) || 
    l.endpoint.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.method.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="h-5 w-5 text-[#00f0ff]" /> API Traffic Monitoring Audit Logs
          </h2>
          <p className="text-xs text-slate-400 mt-1">Real-time HTTP traffic captured automatically by backend middleware</p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Filter IP or Endpoint..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#121824] border border-slate-700/80 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#00f0ff]"
          />
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-5">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm font-mono">Loading traffic logs...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#0f141f] text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Time</th>
                  <th className="py-3 px-4">IP Address</th>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4">Endpoint</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4">Risk Score</th>
                  <th className="py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">{log.timestamp}</td>
                    <td className="py-3 px-4 font-bold text-slate-200">{log.ip_address}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        log.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                        log.method === 'POST' ? 'bg-emerald-500/20 text-emerald-400' :
                        'bg-purple-500/20 text-purple-400'
                      }`}>
                        {log.method}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-[#00f0ff] font-semibold">{log.endpoint}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        log.status_code === 200 || log.status_code === 201 ? 'bg-emerald-500/20 text-emerald-400' :
                        log.status_code === 401 ? 'bg-amber-500/20 text-amber-400' :
                        'bg-rose-500/20 text-rose-400'
                      }`}>
                        {log.status_code}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">{log.response_time_ms} ms</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        log.risk_score >= 70 ? 'bg-rose-500/20 text-rose-400' :
                        log.risk_score >= 35 ? 'bg-amber-500/20 text-amber-400' :
                        'bg-emerald-500/20 text-emerald-400'
                      }`}>
                        {log.risk_score} / 100
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        log.action_taken === 'BLOCKED' ? 'bg-red-600/30 text-red-400 border border-red-500/40' :
                        log.action_taken === 'RATE_LIMIT' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-emerald-500/10 text-emerald-400'
                      }`}>
                        {log.action_taken}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-800 text-xs text-slate-400">
          <div>Page {page} of {totalPages}</div>
          <div className="flex space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 disabled:opacity-40 transition"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(p => p + 1)}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 disabled:opacity-40 transition"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

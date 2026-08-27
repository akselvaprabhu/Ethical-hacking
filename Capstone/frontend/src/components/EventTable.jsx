import React from 'react';
import { AlertCircle, ShieldAlert, ShieldCheck, Zap } from 'lucide-react';

export default function EventTable({ events }) {
  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 text-sm">
        No security events recorded. All API traffic is clean.
      </div>
    );
  }

  const getRiskBadge = (level, score) => {
    switch (level) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-rose-500/20 text-rose-400 border border-rose-500/40">CRITICAL ({score})</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-orange-500/20 text-orange-400 border border-orange-500/40">HIGH ({score})</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-500/20 text-amber-400 border border-amber-500/40">MEDIUM ({score})</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">LOW ({score})</span>;
    }
  };

  const getActionBadge = (action) => {
    switch (action) {
      case 'BLOCK':
      case 'BLOCKED':
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-red-600/30 text-red-300 border border-red-500/50 flex items-center gap-1 w-max"><ShieldAlert className="h-3 w-3"/> BLOCKED</span>;
      case 'RATE_LIMIT':
      case 'LIMITED':
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-500/30 text-amber-300 border border-amber-500/50 flex items-center gap-1 w-max"><Zap className="h-3 w-3"/> LIMITED</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 flex items-center gap-1 w-max"><ShieldCheck className="h-3 w-3"/> ALLOWED</span>;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="bg-[#0f141f] text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
          <tr>
            <th className="py-3 px-4">Time</th>
            <th className="py-3 px-4">IP Address</th>
            <th className="py-3 px-4">Endpoint</th>
            <th className="py-3 px-4">Attack Type</th>
            <th className="py-3 px-4">Risk Level</th>
            <th className="py-3 px-4">Detection Engine</th>
            <th className="py-3 px-4">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 font-mono">
          {events.map((event) => (
            <tr key={event.id} className="hover:bg-slate-800/40 transition">
              <td className="py-3 px-4 text-slate-400 whitespace-nowrap">{event.timestamp}</td>
              <td className="py-3 px-4 font-bold text-slate-200">{event.ip_address}</td>
              <td className="py-3 px-4 text-[#00f0ff]">{event.endpoint}</td>
              <td className="py-3 px-4 text-slate-200 font-semibold">{event.attack_type}</td>
              <td className="py-3 px-4 whitespace-nowrap">{getRiskBadge(event.risk_level, event.risk_score)}</td>
              <td className="py-3 px-4">
                <span className="px-2 py-0.5 text-[10px] rounded bg-purple-500/10 text-purple-300 border border-purple-500/30">
                  {event.detection_method}
                </span>
              </td>
              <td className="py-3 px-4 whitespace-nowrap">{getActionBadge(event.action_taken)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

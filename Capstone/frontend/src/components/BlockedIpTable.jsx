import React from 'react';
import { Lock, Unlock } from 'lucide-react';

export default function BlockedIpTable({ blockedIps, onUnblock }) {
  if (!blockedIps || blockedIps.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 text-sm">
        No active IP blocks registered in firewall.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="bg-[#0f141f] text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
          <tr>
            <th className="py-3 px-4">Blocked IP</th>
            <th className="py-3 px-4">Reason / Threat</th>
            <th className="py-3 px-4">Blocked At</th>
            <th className="py-3 px-4">Expires At</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 font-mono">
          {blockedIps.map((item) => (
            <tr key={item.id} className="hover:bg-slate-800/40 transition">
              <td className="py-3 px-4 font-bold text-rose-400 flex items-center gap-1.5">
                <Lock className="h-3.5 w-3.5" />
                {item.ip_address}
              </td>
              <td className="py-3 px-4 text-slate-300 max-w-xs truncate" title={item.reason}>{item.reason}</td>
              <td className="py-3 px-4 text-slate-400">{item.blocked_at}</td>
              <td className="py-3 px-4 text-slate-400">{item.expires_at}</td>
              <td className="py-3 px-4">
                {item.is_active ? (
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/20 text-rose-400 border border-rose-500/40">
                    ACTIVE BLOCK
                  </span>
                ) : (
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-800 text-slate-400">
                    EXPIRED
                  </span>
                )}
              </td>
              <td className="py-3 px-4 text-right">
                {item.is_active && (
                  <button
                    onClick={() => onUnblock(item.ip_address)}
                    className="px-2.5 py-1 bg-[#00f0ff]/10 hover:bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 rounded text-[11px] font-semibold transition flex items-center gap-1 ml-auto"
                  >
                    <Unlock className="h-3 w-3" />
                    Unblock
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

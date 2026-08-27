import React, { useEffect, useState } from 'react';
import { fetchBlockedIps, unblockIpAddress, blockIpAddressManual } from '../services/api';
import BlockedIpTable from '../components/BlockedIpTable';
import { Lock, Plus, ShieldAlert } from 'lucide-react';

export default function BlockedIps() {
  const [blockedList, setBlockedList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ipInput, setIpInput] = useState('');
  const [reasonInput, setReasonInput] = useState('');
  const [msg, setMsg] = useState(null);

  const loadBlockedIps = async () => {
    try {
      const res = await fetchBlockedIps();
      if (res.success) setBlockedList(res.blocked_ips);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBlockedIps();
  }, []);

  const handleUnblock = async (ip) => {
    await unblockIpAddress(ip);
    setMsg({ type: 'success', text: `IP ${ip} unblocked successfully.` });
    loadBlockedIps();
  };

  const handleManualBlock = async (e) => {
    e.preventDefault();
    if (!ipInput) return;
    const res = await blockIpAddressManual(ipInput, reasonInput || 'Manual Admin Firewall Restriction');
    if (res.success) {
      setMsg({ type: 'success', text: res.message });
      setIpInput('');
      setReasonInput('');
      loadBlockedIps();
    } else {
      setMsg({ type: 'error', text: res.message });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Lock className="h-5 w-5 text-rose-400" /> Active Runtime Protection & Firewall Bans
        </h2>
        <p className="text-xs text-slate-400 mt-1">IP addresses automatically blocked by the decision engine or manually flagged by SOC administrators</p>
      </div>

      {/* Manual IP Block Form */}
      <div className="glass-panel p-5 rounded-2xl space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-rose-400" /> Manual IP Ban Controller
        </h3>

        {msg && (
          <div className={`p-3 rounded-lg text-xs font-semibold ${msg.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'}`}>
            {msg.text}
          </div>
        )}

        <form onSubmit={handleManualBlock} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Target IP Address (e.g. 192.168.1.50)"
            value={ipInput}
            onChange={(e) => setIpInput(e.target.value)}
            className="bg-[#0f141f] border border-slate-700/80 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500 flex-1 font-mono"
            required
          />
          <input
            type="text"
            placeholder="Reason for restriction..."
            value={reasonInput}
            onChange={(e) => setReasonInput(e.target.value)}
            className="bg-[#0f141f] border border-slate-700/80 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500 flex-1"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5 whitespace-nowrap"
          >
            <Plus className="h-4 w-4" /> Enforce IP Block
          </button>
        </form>
      </div>

      {/* Blocked IP Table */}
      <div className="glass-panel rounded-2xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Firewall Rules Audit</h3>
        {loading ? (
          <div className="p-12 text-center text-slate-500 font-mono text-sm">Loading firewall status...</div>
        ) : (
          <BlockedIpTable blockedIps={blockedList} onUnblock={handleUnblock} />
        )}
      </div>
    </div>
  );
}

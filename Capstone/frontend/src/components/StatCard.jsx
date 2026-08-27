import React from 'react';

export default function StatCard({ title, value, icon: Icon, color = 'blue', subtitle }) {
  const colorMap = {
    blue: 'border-[#00f0ff]/30 text-[#00f0ff] bg-[#00f0ff]/5',
    green: 'border-emerald-500/30 text-emerald-400 bg-emerald-500/5',
    yellow: 'border-amber-500/30 text-amber-400 bg-amber-500/5',
    red: 'border-rose-500/30 text-rose-400 bg-rose-500/5',
    purple: 'border-purple-500/30 text-purple-400 bg-purple-500/5'
  };

  return (
    <div className="glass-panel p-5 rounded-xl relative overflow-hidden transition-all duration-300 hover:border-slate-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider font-semibold text-slate-400">{title}</p>
          <h3 className="text-2xl font-bold text-slate-100 font-mono mt-1">{value}</h3>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg border ${colorMap[color] || colorMap.blue}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

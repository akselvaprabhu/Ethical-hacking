import React, { useEffect, useState } from 'react';
import { fetchSecurityEvents } from '../services/api';
import EventTable from '../components/EventTable';
import { AlertTriangle, Cpu, ShieldCheck } from 'lucide-react';

export default function SecurityEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadEvents = async () => {
    try {
      const res = await fetchSecurityEvents();
      if (res.success) setEvents(res.events);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-400" /> Security Threat Detections & Incidents
        </h2>
        <p className="text-xs text-slate-400 mt-1">Detailed analysis of signature matches, brute force attempts, and ML statistical anomalies</p>
      </div>

      {/* Detection Engine Explanation Box */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-panel p-4 rounded-xl border-l-4 border-l-[#00f0ff] space-y-2">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-[#00f0ff]" /> Signature & Rule-Based Engine
          </h3>
          <p className="text-xs text-slate-400">
            Inspects request path, query string, payload body, and failed authentication counters against pre-configured patterns (SQLi, XSS, Path Traversal, Brute Force).
          </p>
        </div>
        <div className="glass-panel p-4 rounded-xl border-l-4 border-l-purple-500 space-y-2">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-purple-400" /> ML Isolation Forest Engine
          </h3>
          <p className="text-xs text-slate-400">
            Evaluates request frequency, status 4xx/5xx ratios, and auth failure densities against a baseline model to detect unknown behavioral anomalies.
          </p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Incident Telemetry Log</h3>
        {loading ? (
          <div className="p-12 text-center text-slate-500 font-mono text-sm">Loading security events...</div>
        ) : (
          <EventTable events={events} />
        )}
      </div>
    </div>
  );
}

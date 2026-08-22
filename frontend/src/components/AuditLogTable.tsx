import React, { useState, useEffect } from 'react';
import { ScrollText, Filter, RefreshCw, Loader2, ShieldCheck } from 'lucide-react';
import { AuditLogEntry } from '../types';
import { fetchAuditLogs } from '../services/api';

export const AuditLogTable: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [eventTypeFilter, setEventTypeFilter] = useState('ALL');

  useEffect(() => {
    loadLogs();
  }, [eventTypeFilter]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const params = eventTypeFilter !== 'ALL' ? { event_type: eventTypeFilter } : undefined;
      const res = await fetchAuditLogs(params);
      setLogs(res);
    } catch (e: any) {
      console.error('Audit log fetch failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Compliance & System Audit Trail</span>
          </h3>
          <p className="text-xs text-slate-500">
            Immutable log of system actions, candidate status updates, and PII revelations
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-md px-2.5 py-1.5 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Event Types</option>
            <option value="RESUME_UPLOAD">Resume Upload</option>
            <option value="RESUME_PARSED">Resume Parsed</option>
            <option value="SCREENING_STARTED">Screening Started</option>
            <option value="SCORE_CALCULATED">Score Calculated</option>
            <option value="STATUS_CHANGED">Status Changed</option>
            <option value="RECRUITER_NOTE_ADDED">Recruiter Note</option>
            <option value="PII_REVEALED">PII Revealed</option>
            <option value="CANDIDATES_COMPARED">Candidates Compared</option>
          </select>

          <button
            onClick={loadLogs}
            className="p-1.5 rounded border border-slate-200 hover:bg-slate-50 text-slate-600"
            title="Refresh logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Log Table */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 text-[11px] font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-3">Event Type</th>
                <th className="py-2.5 px-3">Actor</th>
                <th className="py-2.5 px-3">Candidate / Job</th>
                <th className="py-2.5 px-4">Event Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600 mx-auto mb-1" />
                    Loading audit trail...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No audit records recorded yet.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.log_id} className="hover:bg-slate-50/50">
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-3">
                      <span className="font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded text-[10px]">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-900">{log.actor}</td>
                    <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">
                      {log.candidate_id ? `cand:${log.candidate_id.slice(0, 8)}` : log.job_id ? `job:${log.job_id.slice(0, 8)}` : '—'}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600 max-w-md truncate">
                      {JSON.stringify(log.details)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

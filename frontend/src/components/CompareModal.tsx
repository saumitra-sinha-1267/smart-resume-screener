import React, { useState, useEffect } from 'react';
import { X, Users, CheckCircle2, AlertTriangle, XCircle, HelpCircle, Loader2 } from 'lucide-react';
import { CandidateComparisonResponse } from '../types';
import { compareCandidates } from '../services/api';

interface CompareModalProps {
  candidateIds: string[];
  jobId: string;
  onClose: () => void;
}

export const CompareModal: React.FC<CompareModalProps> = ({ candidateIds, jobId, onClose }) => {
  const [data, setData] = useState<CandidateComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadComparison();
  }, [candidateIds, jobId]);

  const loadComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await compareCandidates(candidateIds, jobId);
      setData(res);
    } catch (e: any) {
      setError(e.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xl w-full max-w-5xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Candidate Comparison Matrix — {data?.job_title || 'Position Evaluation'}
            </h3>
          </div>
          <button onClick={onClose} aria-label="Close modal" className="p-1 rounded text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-5 flex-1 text-xs">
          {loading ? (
            <div className="p-12 text-center space-y-2">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600 mx-auto" />
              <p className="text-slate-500">Generating side-by-side comparison...</p>
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-50 text-rose-700 border border-rose-200 rounded-md">
              {error}
            </div>
          ) : data ? (
            <>
              {/* Recommendation Strip */}
              <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-lg">
                <span className="text-[11px] font-bold text-blue-900 uppercase tracking-wider block mb-1">
                  AI Shortlist Synthesis
                </span>
                <p className="text-xs text-slate-800">{data.recommendation}</p>
              </div>

              {/* Side-by-side Candidate Headers */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {data.candidates.map((c) => (
                  <div key={c.candidate_id} className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-sm text-slate-900">{c.candidate_name}</h4>
                      <span className="text-xs font-black text-blue-600">{c.overall_score.toFixed(1)}/10</span>
                    </div>

                    <div className="text-[11px] text-slate-500 space-y-0.5">
                      <p>Mandatory Met: <strong>{c.matched_mandatory_count}/{c.total_mandatory_count}</strong></p>
                      <p>Strong Evidence: <strong>{c.strong_evidence_count} metrics</strong></p>
                    </div>

                    <div className="pt-2 border-t border-slate-200 space-y-1">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Strengths:</span>
                      {c.top_strengths.map((s, idx) => (
                        <p key={idx} className="text-[11px] text-emerald-700">✓ {s}</p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Requirement Matrix Table */}
              <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
                <div className="px-4 py-2.5 bg-slate-50 border-b border-slate-200 font-bold text-slate-700 text-xs">
                  Detailed Criteria Matrix
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50/70 text-slate-500 text-[11px] font-semibold uppercase border-b border-slate-200">
                      <tr>
                        <th className="py-2.5 px-3">Requirement</th>
                        {data.candidates.map((c) => (
                          <th key={c.candidate_id} className="py-2.5 px-3">
                            {c.candidate_name}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {data.side_by_side_matrix.map((row) => (
                        <tr key={row.requirement_id} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-semibold text-slate-900 max-w-xs">
                            {row.text}
                          </td>
                          {data.candidates.map((c) => {
                            const evalObj = row.evaluations[c.candidate_id];
                            return (
                              <td key={c.candidate_id} className="py-2.5 px-3 text-xs">
                                {evalObj ? (
                                  <span
                                    className={`font-semibold px-2 py-0.5 rounded text-[11px] ${
                                      evalObj.status === 'MATCHED'
                                        ? 'bg-emerald-50 text-emerald-700'
                                        : evalObj.status === 'PARTIAL'
                                        ? 'bg-amber-50 text-amber-700'
                                        : evalObj.status === 'INFERRED'
                                        ? 'bg-blue-50 text-blue-700'
                                        : 'bg-rose-50 text-rose-700'
                                    }`}
                                  >
                                    {evalObj.status}
                                  </span>
                                ) : (
                                  <span className="text-slate-400">—</span>
                                )}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

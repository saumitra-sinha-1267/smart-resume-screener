import React from 'react';
import { RequirementMatch } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

interface RequirementMatrixProps {
  matches: RequirementMatch[];
}

export const RequirementMatrix: React.FC<RequirementMatrixProps> = ({ matches }) => {
  if (!matches || matches.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg">
        No specific requirement matrix evaluated yet.
      </div>
    );
  }

  const getStatusBadge = (status: RequirementMatch['status']) => {
    switch (status) {
      case 'MATCHED':
        return (
          <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
            MATCHED
          </span>
        );
      case 'PARTIAL':
        return (
          <span className="inline-flex items-center text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
            <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" />
            PARTIAL
          </span>
        );
      case 'INFERRED':
        return (
          <span className="inline-flex items-center text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">
            <HelpCircle className="w-3 h-3 mr-1 text-blue-600" />
            INFERRED
          </span>
        );
      case 'MISSING':
      default:
        return (
          <span className="inline-flex items-center text-[11px] font-semibold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded">
            <XCircle className="w-3 h-3 mr-1 text-rose-600" />
            MISSING
          </span>
        );
    }
  };

  const getStrengthBadge = (strength: RequirementMatch['evidence_strength']) => {
    if (strength === 'STRONG') {
      return <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">STRONG</span>;
    }
    if (strength === 'MEDIUM') {
      return <span className="text-[10px] font-medium text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">MEDIUM</span>;
    }
    if (strength === 'WEAK') {
      return <span className="text-[10px] font-medium text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">WEAK</span>;
    }
    return <span className="text-[10px] text-slate-400">—</span>;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
          Job Requirement Evaluation Matrix
        </h4>
        <span className="text-xs text-slate-500 font-medium">{matches.length} Criteria Evaluated</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-slate-50/70 text-slate-500 border-b border-slate-200 text-[11px] font-semibold uppercase tracking-wider">
            <tr>
              <th className="py-2.5 px-4">Requirement</th>
              <th className="py-2.5 px-3">Type</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Evidence Strength</th>
              <th className="py-2.5 px-4">Supporting Evidence / Reasoning</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {matches.map((req, idx) => (
              <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                <td className="py-3 px-4 font-semibold text-slate-900 max-w-xs">
                  {req.text}
                </td>
                <td className="py-3 px-3">
                  <span
                    className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                      req.is_mandatory
                        ? 'bg-rose-50 text-rose-700 border border-rose-200'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {req.is_mandatory ? 'Hard' : 'Soft'}
                  </span>
                </td>
                <td className="py-3 px-3">{getStatusBadge(req.status)}</td>
                <td className="py-3 px-3">{getStrengthBadge(req.evidence_strength)}</td>
                <td className="py-3 px-4 text-xs text-slate-600">
                  <p>{req.reasoning}</p>
                  {req.supporting_evidence && req.supporting_evidence.length > 0 && (
                    <div className="mt-1 space-y-0.5">
                      {req.supporting_evidence.map((ev, evIdx) => (
                        <p key={evIdx} className="text-[11px] text-slate-500 italic bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                          "{ev}"
                        </p>
                      ))}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

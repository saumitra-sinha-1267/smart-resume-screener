import React from 'react';
import { ClaimVerification } from '../types';
import { ShieldCheck, ShieldAlert, Check, X } from 'lucide-react';

interface ClaimAuditTableProps {
  claims?: ClaimVerification[];
}

export const ClaimAuditTable: React.FC<ClaimAuditTableProps> = ({ claims }) => {
  if (!claims || claims.length === 0) {
    return (
      <div className="p-4 text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg text-center">
        No specific AI claims audited for this profile.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          <span>AI Claim Verification & Hallucination Guard</span>
        </h4>
        <span className="text-xs text-slate-500">{claims.length} Claims Audited</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/70 text-slate-500 text-[11px] font-semibold uppercase tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-2.5 px-4">AI Claim</th>
              <th className="py-2.5 px-4">Ground Truth Evidence</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3 text-right">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {claims.map((c, idx) => (
              <tr key={idx} className="hover:bg-slate-50/50">
                <td className="py-3 px-4 font-medium text-slate-900">{c.claim}</td>
                <td className="py-3 px-4 text-slate-600 italic">"{c.evidence}"</td>
                <td className="py-3 px-3">
                  {c.verification_status === 'VERIFIED' ? (
                    <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                      <Check className="w-3 h-3 mr-1" />
                      VERIFIED
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-[11px] font-semibold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded">
                      <X className="w-3 h-3 mr-1" />
                      UNVERIFIED
                    </span>
                  )}
                </td>
                <td className="py-3 px-3 text-right font-mono font-bold text-slate-900">
                  {Math.round(c.confidence * 100)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

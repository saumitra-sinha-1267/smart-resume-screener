import React from 'react';
import { CandidateData } from '../types';
import { Percent, ShieldCheck, CheckCircle, Award } from 'lucide-react';

interface EvidencePanelProps {
  candidate: CandidateData;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ candidate }) => {
  const strongBullets: string[] = [];
  const mediumBullets: string[] = [];
  const weakBullets: string[] = [];

  const metricRegex = /\b\d+(?:\.\d+)?%|\b\d+\s*ms|\b\d+[kKmMbB]|\b\$\d+/;

  candidate.experience.forEach((exp) => {
    exp.bullets.forEach((b) => {
      if (metricRegex.test(b)) {
        strongBullets.push(b);
      } else if (b.length >= 40) {
        mediumBullets.push(b);
      } else {
        weakBullets.push(b);
      }
    });
  });

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
          <Award className="w-4 h-4 text-blue-600" />
          <span>Resume Evidence Quality Audit</span>
        </h4>
        <span className="text-xs text-slate-500">
          {strongBullets.length} Strong • {mediumBullets.length} Medium • {weakBullets.length} Weak
        </span>
      </div>

      {/* Strong Quantified Evidence */}
      {strongBullets.length > 0 && (
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider flex items-center space-x-1">
            <Percent className="w-3.5 h-3.5 text-emerald-600" />
            <span>Strong Quantified Outcomes ({strongBullets.length})</span>
          </span>
          <div className="space-y-1.5">
            {strongBullets.map((b, idx) => (
              <div key={idx} className="p-2 bg-emerald-50/50 border border-emerald-100 rounded text-xs text-slate-800 leading-relaxed">
                {b}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medium Technical Evidence */}
      {mediumBullets.length > 0 && (
        <div className="space-y-2">
          <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1">
            <CheckCircle className="w-3.5 h-3.5 text-slate-500" />
            <span>Technical Implementations ({mediumBullets.length})</span>
          </span>
          <div className="space-y-1.5">
            {mediumBullets.slice(0, 4).map((b, idx) => (
              <div key={idx} className="p-2 bg-slate-50 border border-slate-100 rounded text-xs text-slate-700 leading-relaxed">
                {b}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

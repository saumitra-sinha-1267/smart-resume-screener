import React from 'react';
import { ScoreOutput } from '../types';

interface ScoreBreakdownProps {
  score: ScoreOutput;
}

export const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({ score }) => {
  const overallPercent = Math.round((score.overall_score / 10) * 100);
  const skillsPercent = Math.round((score.skills_match.score / 10) * 100);
  const expPercent = Math.round((score.experience_relevance.score / 10) * 100);
  const evidencePercent = score.evidence_score
    ? Math.round((score.evidence_score.score / 10) * 100)
    : 75;
  const seniorityPercent = Math.round((score.seniority_alignment.score / 10) * 100);
  const eduPercent = Math.round((score.education_fit.score / 10) * 100);

  const getBarColor = (pct: number) => {
    if (pct >= 80) return 'bg-emerald-500';
    if (pct >= 60) return 'bg-blue-600';
    if (pct >= 40) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const dimensions = [
    { label: 'Skills Alignment (30%)', score: score.skills_match.score, pct: skillsPercent },
    { label: 'Experience Depth (25%)', score: score.experience_relevance.score, pct: expPercent },
    { label: 'Evidence Quality (20%)', score: score.evidence_score?.score ?? 7.5, pct: evidencePercent },
    { label: 'Seniority Match (15%)', score: score.seniority_alignment.score, pct: seniorityPercent },
    { label: 'Education Fit (10%)', score: score.education_fit.score, pct: eduPercent },
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-4">
      {/* Overall Score Highlight */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <span className="text-[11px] font-semibold uppercase text-slate-500 tracking-wider">Overall Match</span>
          <div className="flex items-baseline space-x-2 mt-0.5">
            <span className="text-2xl font-black text-slate-900">{score.overall_score.toFixed(1)}</span>
            <span className="text-xs text-slate-500 font-medium">/ 10 ({overallPercent}%)</span>
          </div>
        </div>
        <div className="text-right">
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded border ${
              score.scoring_method === 'llm'
                ? 'bg-blue-50 text-blue-700 border-blue-200'
                : 'bg-slate-100 text-slate-700 border-slate-200'
            }`}
          >
            {score.scoring_method === 'llm' ? 'AI Evaluated' : 'Rule Engine'}
          </span>
          <p className="text-[10px] text-slate-400 mt-1">
            {score.hard_requirements_passed ? '✓ Hard Criteria Met' : '⚠ Hard Gaps'}
          </p>
        </div>
      </div>

      {/* Sub-Dimension Progress Bars */}
      <div className="space-y-3">
        {dimensions.map((dim, idx) => (
          <div key={idx} className="space-y-1">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-slate-600">{dim.label}</span>
              <span className="text-slate-900 font-bold">{dim.score.toFixed(1)} / 10</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full ${getBarColor(dim.pct)} progress-bar-fill`}
                style={{ width: `${Math.min(100, Math.max(0, dim.pct))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

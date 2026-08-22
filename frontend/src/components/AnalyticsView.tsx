import React from 'react';
import { ScreeningResult } from '../types';
import { BarChart3, TrendingUp, Users, CheckCircle2, Award, Zap } from 'lucide-react';
import { KpiCard } from './KpiCard';

interface AnalyticsViewProps {
  results: ScreeningResult[];
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ results }) => {
  const total = results.length;
  const screened = results.filter((r) => r.candidate.status !== 'NEW').length;
  const shortlisted = results.filter((r) => r.candidate.status === 'SHORTLISTED').length;
  const interviews = results.filter((r) => r.candidate.status === 'INTERVIEW').length;

  const avgScore = total > 0 ? results.reduce((acc, r) => acc + r.score.overall_score, 0) / total : 0;
  const highConfCount = results.filter((r) => r.score.confidence === 'High').length;
  const confRate = total > 0 ? Math.round((highConfCount / total) * 100) : 0;

  // Top skills count
  const skillCounts: Record<string, number> = {};
  results.forEach((r) => {
    r.candidate.skills.forEach((s) => {
      skillCounts[s.name] = (skillCounts[s.name] || 0) + 1;
    });
  });
  const topSkills = Object.entries(skillCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  // Score distribution brackets
  const scoreBrackets = {
    '9.0 - 10.0': results.filter((r) => r.score.overall_score >= 9.0).length,
    '7.5 - 8.9': results.filter((r) => r.score.overall_score >= 7.5 && r.score.overall_score < 9.0).length,
    '6.0 - 7.4': results.filter((r) => r.score.overall_score >= 6.0 && r.score.overall_score < 7.5).length,
    '< 6.0': results.filter((r) => r.score.overall_score < 6.0).length,
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Candidates Screened"
          value={screened}
          subtitle={`Across ${total} total profiles`}
          icon={Users}
          iconBg="bg-blue-50"
          iconColor="text-blue-600"
        />
        <KpiCard
          title="Average Match Score"
          value={`${avgScore.toFixed(1)} / 10`}
          subtitle="Multi-dimension composite"
          icon={Award}
          iconBg="bg-emerald-50"
          iconColor="text-emerald-600"
        />
        <KpiCard
          title="Shortlist Conversion"
          value={total > 0 ? `${Math.round((shortlisted / total) * 100)}%` : '0%'}
          subtitle={`${shortlisted} candidates shortlisted`}
          icon={TrendingUp}
          iconBg="bg-purple-50"
          iconColor="text-purple-600"
        />
        <KpiCard
          title="High Confidence Rate"
          value={`${confRate}%`}
          subtitle={`${highConfCount} verified profiles`}
          icon={Zap}
          iconBg="bg-amber-50"
          iconColor="text-amber-600"
        />
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution Chart */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-4">
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Match Score Distribution
          </h4>
          <div className="space-y-3 pt-2">
            {Object.entries(scoreBrackets).map(([label, count]) => {
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              return (
                <div key={label} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-600">{label}</span>
                    <span className="text-slate-900 font-bold">{count} candidates ({pct}%)</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="h-2 rounded-full bg-blue-600" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Extracted Skills */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-4">
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Top Skills in Candidate Pool
          </h4>
          <div className="space-y-3 pt-2">
            {topSkills.map(([skill, count]) => {
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              return (
                <div key={skill} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-600 font-semibold">{skill}</span>
                    <span className="text-slate-900 font-bold">{count} profiles</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="h-2 rounded-full bg-emerald-500" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

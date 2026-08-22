import React from 'react';
import { Calendar, User, Clock, CheckCircle } from 'lucide-react';
import { ScreeningResult } from '../types';
import { StatusBadge } from './StatusBadge';

interface InterviewsViewProps {
  results: ScreeningResult[];
  anonymized: boolean;
  onSelectResult: (res: ScreeningResult) => void;
}

export const InterviewsView: React.FC<InterviewsViewProps> = ({
  results,
  anonymized,
  onSelectResult,
}) => {
  const interviewees = results.filter((r) => r.candidate.status === 'INTERVIEW');

  return (
    <div className="space-y-4">
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-blue-600" />
            <span>Interview Schedule Docket</span>
          </h3>
          <p className="text-xs text-slate-500">
            Candidates currently moved into active technical screening or hiring manager rounds
          </p>
        </div>
        <span className="text-xs font-semibold text-purple-700 bg-purple-50 border border-purple-200 px-2.5 py-1 rounded">
          {interviewees.length} Scheduled
        </span>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 text-[11px] font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-4">Candidate</th>
                <th className="py-2.5 px-3">Role</th>
                <th className="py-2.5 px-3">Overall Score</th>
                <th className="py-2.5 px-3">Interviewer</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {interviewees.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No candidates currently in the interview stage. Shortlist and promote candidates from the dashboard.
                  </td>
                </tr>
              ) : (
                interviewees.map((res) => {
                  const displayName = anonymized
                    ? res.candidate.anonymized_name || `Candidate #${res.candidate.candidate_id.slice(0, 6)}`
                    : res.candidate.raw_name || 'Anonymous';
                  return (
                    <tr key={res.candidate.candidate_id} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-semibold text-slate-900">{displayName}</td>
                      <td className="py-3 px-3 text-slate-600">
                        {res.candidate.experience[0]?.title || 'Software Engineer'}
                      </td>
                      <td className="py-3 px-3 font-bold text-blue-600">
                        {res.score.overall_score.toFixed(1)}/10
                      </td>
                      <td className="py-3 px-3 text-slate-600">Sarah Jenkins (Lead)</td>
                      <td className="py-3 px-3">
                        <StatusBadge status="INTERVIEW" />
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => onSelectResult(res)}
                          className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 font-semibold text-xs hover:bg-blue-100"
                        >
                          View Dossier
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

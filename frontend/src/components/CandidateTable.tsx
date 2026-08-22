import React, { useState } from 'react';
import {
  Search,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Trash2,
  Eye,
  CheckSquare,
  Square,
  Users
} from 'lucide-react';
import { ScreeningResult, JobData, CandidateStatus } from '../types';
import { StatusBadge } from './StatusBadge';
import { ConfidenceBadge } from './ConfidenceBadge';

interface CandidateTableProps {
  results: ScreeningResult[];
  jobs: JobData[];
  selectedJobId?: string;
  onSelectJobId?: (id: string) => void;
  anonymized: boolean;
  onSelectResult: (res: ScreeningResult) => void;
  onDeleteCandidate?: (candidateId: string) => void;
  onBulkStatusUpdate?: (candidateIds: string[], status: CandidateStatus) => void;
  onCompareCandidates?: (candidateIds: string[]) => void;
  isScreening: boolean;
  onRunScreening: () => void;
}

export const CandidateTable: React.FC<CandidateTableProps> = ({
  results,
  jobs,
  selectedJobId,
  onSelectJobId,
  anonymized,
  onSelectResult,
  onDeleteCandidate,
  onBulkStatusUpdate,
  onCompareCandidates,
  isScreening,
  onRunScreening,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [scoreFilter, setScoreFilter] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<'score' | 'experience' | 'name'>('score');
  const [sortAsc, setSortAsc] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Filter & Search Logic
  const filtered = results.filter((r) => {
    const name = anonymized ? r.candidate.anonymized_name : r.candidate.raw_name;
    const matchesSearch =
      (name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.score.skills_match.matched.some((m) => m.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus = statusFilter === 'ALL' || r.candidate.status === statusFilter;
    const matchesScore =
      scoreFilter === 'ALL' ||
      (scoreFilter === 'HIGH' && r.score.overall_score >= 8.0) ||
      (scoreFilter === 'MID' && r.score.overall_score >= 6.0 && r.score.overall_score < 8.0) ||
      (scoreFilter === 'LOW' && r.score.overall_score < 6.0);

    return matchesSearch && matchesStatus && matchesScore;
  });

  // Sorting
  filtered.sort((a, b) => {
    let diff = 0;
    if (sortBy === 'score') diff = b.score.overall_score - a.score.overall_score;
    else if (sortBy === 'experience') diff = b.candidate.total_experience_years - a.candidate.total_experience_years;
    else diff = (a.candidate.raw_name || '').localeCompare(b.candidate.raw_name || '');
    return sortAsc ? -diff : diff;
  });

  // Pagination
  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const paginated = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const toggleSelectAll = () => {
    if (selectedIds.length === paginated.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(paginated.map((p) => p.candidate.candidate_id));
    }
  };

  const toggleSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((x) => x !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
      {/* Table Control Bar */}
      <div className="p-4 border-b border-slate-200 flex flex-col lg:flex-row lg:items-center justify-between gap-3 bg-slate-50/50">
        <div className="flex flex-wrap items-center gap-2">
          {/* Search input */}
          <div className="relative w-56">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search candidate / skill..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
          </div>

          {/* Job Filter */}
          {jobs.length > 0 && onSelectJobId && (
            <select
              value={selectedJobId || ''}
              onChange={(e) => onSelectJobId(e.target.value)}
              className="text-xs bg-white border border-slate-200 rounded-md px-2.5 py-1.5 text-slate-700 focus:outline-none"
            >
              {jobs.map((j) => (
                <option key={j.job_id} value={j.job_id}>
                  Role: {j.title}
                </option>
              ))}
            </select>
          )}

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-md px-2.5 py-1.5 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="SCREENED">Screened</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="SHORTLISTED">Shortlisted</option>
            <option value="INTERVIEW">Interview</option>
            <option value="REJECTED">Rejected</option>
          </select>

          {/* Score Filter */}
          <select
            value={scoreFilter}
            onChange={(e) => setScoreFilter(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-md px-2.5 py-1.5 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Scores</option>
            <option value="HIGH">Score 8.0+ (Strong)</option>
            <option value="MID">Score 6.0 - 7.9 (Moderate)</option>
            <option value="LOW">Score &lt; 6.0 (Gaps)</option>
          </select>
        </div>

        {/* Action Controls & Bulk Buttons */}
        <div className="flex items-center space-x-2">
          {selectedIds.length > 1 && onCompareCandidates && (
            <button
              onClick={() => onCompareCandidates(selectedIds)}
              className="px-3 py-1.5 rounded bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold flex items-center space-x-1 hover:bg-blue-100 transition-colors"
            >
              <Users className="w-3.5 h-3.5" />
              <span>Compare ({selectedIds.length})</span>
            </button>
          )}

          {selectedIds.length > 0 && onBulkStatusUpdate && (
            <button
              onClick={() => onBulkStatusUpdate(selectedIds, 'SHORTLISTED')}
              className="px-3 py-1.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold hover:bg-emerald-100 transition-colors"
            >
              Shortlist Selected
            </button>
          )}

          <button
            onClick={onRunScreening}
            disabled={isScreening}
            className="px-3.5 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-all disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${isScreening ? 'animate-spin' : ''}`} />
            <span>{isScreening ? 'Screening...' : 'Run Screener'}</span>
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-slate-50 text-slate-500 font-semibold text-[11px] uppercase tracking-wider border-b border-slate-200">
            <tr>
              <th className="py-2.5 px-3 w-8 text-center">
                <button onClick={toggleSelectAll} aria-label="Select all rows">
                  {selectedIds.length > 0 && selectedIds.length === paginated.length ? (
                    <CheckSquare className="w-4 h-4 text-blue-600" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-400" />
                  )}
                </button>
              </th>
              <th className="py-2.5 px-4 cursor-pointer" onClick={() => { setSortBy('name'); setSortAsc(!sortAsc); }}>
                <div className="flex items-center space-x-1">
                  <span>Candidate</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-2.5 px-4 cursor-pointer" onClick={() => { setSortBy('score'); setSortAsc(!sortAsc); }}>
                <div className="flex items-center space-x-1">
                  <span>Match Score</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-2.5 px-3 cursor-pointer" onClick={() => { setSortBy('experience'); setSortAsc(!sortAsc); }}>
                <div className="flex items-center space-x-1">
                  <span>Experience</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-2.5 px-4">Top Skills</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Confidence</th>
              <th className="py-2.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {paginated.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-12 text-center text-slate-500">
                  No candidates found in current pool. Upload resumes or click "Demo Benchmarks".
                </td>
              </tr>
            ) : (
              paginated.map((res) => {
                const displayName = anonymized
                  ? res.candidate.anonymized_name || `Candidate #${res.candidate.candidate_id.slice(0, 6)}`
                  : res.candidate.raw_name || 'Anonymous Candidate';
                const isSelected = selectedIds.includes(res.candidate.candidate_id);
                const scorePercent = Math.round((res.score.overall_score / 10) * 100);

                return (
                  <tr
                    key={res.candidate.candidate_id}
                    onClick={() => onSelectResult(res)}
                    className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                      isSelected ? 'bg-blue-50/40' : ''
                    }`}
                  >
                    {/* Checkbox */}
                    <td className="py-3 px-3 text-center" onClick={(e) => e.stopPropagation()}>
                      <button onClick={() => toggleSelect(res.candidate.candidate_id)}>
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 text-blue-600" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-300 hover:text-slate-400" />
                        )}
                      </button>
                    </td>

                    {/* Candidate Name & Title */}
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900 text-xs">{displayName}</div>
                      <div className="text-[11px] text-slate-500">
                        {res.candidate.experience[0]?.title || 'Software Engineer'}
                      </div>
                    </td>

                    {/* Score Bar */}
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-xs text-slate-900 w-7">
                          {res.score.overall_score.toFixed(1)}
                        </span>
                        <div className="w-20 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-1.5 rounded-full ${
                              scorePercent >= 80 ? 'bg-emerald-500' : scorePercent >= 60 ? 'bg-blue-600' : 'bg-amber-500'
                            }`}
                            style={{ width: `${scorePercent}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Experience */}
                    <td className="py-3 px-3 font-medium text-slate-700">
                      {res.candidate.total_experience_years} yrs
                    </td>

                    {/* Skills */}
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {res.score.skills_match.matched.slice(0, 3).map((sk) => (
                          <span key={sk} className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                            {sk}
                          </span>
                        ))}
                        {res.score.skills_match.matched.length > 3 && (
                          <span className="text-[10px] text-slate-400">+{res.score.skills_match.matched.length - 3}</span>
                        )}
                      </div>
                    </td>

                    {/* Status */}
                    <td className="py-3 px-3">
                      <StatusBadge status={res.candidate.status} />
                    </td>

                    {/* Confidence */}
                    <td className="py-3 px-3">
                      <ConfidenceBadge confidence={res.score.confidence} />
                    </td>

                    {/* Action Buttons */}
                    <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end space-x-1">
                        <button
                          onClick={() => onSelectResult(res)}
                          title="View Profile"
                          className="px-2 py-1 rounded text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
                        >
                          View
                        </button>
                        {onDeleteCandidate && (
                          <button
                            onClick={() => onDeleteCandidate(res.candidate.candidate_id)}
                            title="Delete Candidate"
                            className="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
        <span>
          Showing {paginated.length} of {filtered.length} candidate profiles
        </span>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="px-2 font-medium">Page {currentPage} of {totalPages}</span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-1 rounded border border-slate-200 hover:bg-slate-50 disabled:opacity-40"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

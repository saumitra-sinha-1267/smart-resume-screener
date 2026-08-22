import React, { useState, useEffect } from 'react';
import {
  X,
  CheckCircle2,
  AlertTriangle,
  Send,
  ExternalLink,
  MessageSquare,
  Sparkles,
  Bot,
  Scale
} from 'lucide-react';
import { CandidateData, ScreeningResult, CandidateStatus } from '../types';
import { StatusBadge } from './StatusBadge';
import { ConfidenceBadge } from './ConfidenceBadge';
import { ScoreBreakdown } from './ScoreBreakdown';
import { RequirementMatrix } from './RequirementMatrix';
import { EvidencePanel } from './EvidencePanel';
import { ClaimAuditTable } from './ClaimAuditTable';
import { updateCandidateStatus, addCandidateNote } from '../services/api';

interface CandidateProfileProps {
  result: ScreeningResult | null;
  anonymized: boolean;
  onClose: () => void;
  onCandidateUpdated: (updated: CandidateData) => void;
}

export const CandidateProfile: React.FC<CandidateProfileProps> = ({
  result,
  anonymized,
  onClose,
  onCandidateUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'requirements' | 'evidence' | 'claims' | 'experience' | 'notes'>('overview');
  const [newNoteText, setNewNoteText] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!result) return null;

  const { candidate, score } = result;
  const displayName = anonymized
    ? candidate.anonymized_name || `Candidate #${candidate.candidate_id.slice(0, 6)}`
    : candidate.raw_name || 'Anonymous Candidate';

  const handleStatusChange = async (newStatus: CandidateStatus) => {
    try {
      setIsUpdatingStatus(true);
      const updated = await updateCandidateStatus(candidate.candidate_id, newStatus);
      onCandidateUpdated(updated);
    } catch (e: any) {
      alert(`Status update failed: ${e.message}`);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteText.trim()) return;
    try {
      setIsSubmittingNote(true);
      const updated = await addCandidateNote(candidate.candidate_id, newNoteText, 'Talent Lead');
      onCandidateUpdated(updated);
      setNewNoteText('');
    } catch (e: any) {
      alert(`Note failed: ${e.message}`);
    } finally {
      setIsSubmittingNote(false);
    }
  };

  // Helper to clean requirement text prefix
  const cleanReqText = (txt: string) =>
    txt.replace(/^(?:Demonstrated hands-on expertise with|Hands-on expertise in|Experience or familiarity with|Familiarity with|Expertise in)\s+/i, '').trim();

  // Compute strengths and gaps for "WHY THIS CANDIDATE?" dynamically from requirement matrix
  const strengths: string[] = [];
  const gaps: string[] = [];

  const reqMatches = score.requirement_matches || [];
  const mandSkillReqs = reqMatches.filter((r) => r.category === 'skill' && r.is_mandatory);
  const matchedMandSkills = mandSkillReqs.filter((r) => r.status === 'MATCHED' || r.status === 'INFERRED');
  const prefSkillReqs = reqMatches.filter((r) => r.category === 'skill' && !r.is_mandatory);
  const matchedPrefSkills = prefSkillReqs.filter((r) => r.status === 'MATCHED' || r.status === 'INFERRED');

  if (mandSkillReqs.length > 0) {
    const prefNames = matchedPrefSkills.map((r) => cleanReqText(r.text));
    let strengthMsg = `Matches ${matchedMandSkills.length} of ${mandSkillReqs.length} mandatory skills`;
    if (prefNames.length > 0) {
      strengthMsg += `, with additional experience in ${prefNames.slice(0, 3).join(' and ')}.`;
    } else {
      strengthMsg += '.';
    }
    strengths.push(strengthMsg);
  } else if (score.skills_match.matched.length > 0) {
    strengths.push(`Matches ${score.skills_match.matched.length} key skills: ${score.skills_match.matched.slice(0, 4).join(', ')}`);
  }

  if (candidate.total_experience_years >= 4) {
    strengths.push(`${candidate.total_experience_years} years of verified progressive engineering experience`);
  }
  const strongBulletsCount = candidate.skills.filter((s) => s.quantified_evidence || s.evidence_strength === 'STRONG').length;
  if (strongBulletsCount >= 2) {
    strengths.push(`Demonstrates ${strongBulletsCount} quantified outcome metrics in work history`);
  }
  if (candidate.external_links.some((l) => l.verified === true)) {
    strengths.push('Active public GitHub/portfolio exhibits verified live');
  }

  // Dynamic Gaps from Requirement Matrix
  const missingMandatory = reqMatches.filter((r) => r.is_mandatory && r.status === 'MISSING');
  if (missingMandatory.length > 0) {
    const missingNames = missingMandatory.map((r) => cleanReqText(r.text));
    if (missingNames.length === 1) {
      gaps.push(`One mandatory skill is not evidenced: ${missingNames[0]}.`);
    } else {
      gaps.push(`${missingNames.length} mandatory skills are not evidenced: ${missingNames.join(', ')}.`);
    }
  } else if (score.skills_match.missing.length > 0) {
    gaps.push(`Unconfirmed skill requirements: ${score.skills_match.missing.slice(0, 3).join(', ')}`);
  } else if (!score.hard_requirements_passed) {
    gaps.push('Did not satisfy all mandatory position qualifications.');
  }

  if (!score.hallucination_guard_passed) {
    gaps.push('Hallucination guard detected unverified claim in resume extractions');
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-y-0 right-0 w-full max-w-3xl bg-white border-l border-slate-200 shadow-2xl z-50 overflow-y-auto flex flex-col"
    >
      {/* Header */}
      <div className="p-5 border-b border-slate-200 bg-slate-50 flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold text-slate-900">{displayName}</h2>
            <StatusBadge status={candidate.status} />
            <ConfidenceBadge confidence={score.confidence} />
          </div>

          <p className="text-xs text-slate-500 font-medium">
            {candidate.education[0]?.degree || 'Education Unspecified'} • {candidate.total_experience_years} Years Experience
          </p>

          {!anonymized && candidate.contact.email && (
            <p className="text-xs text-slate-600 font-mono">
              {candidate.contact.email} • {candidate.contact.phone || 'Phone unlisted'}
            </p>
          )}
        </div>

        <div className="flex items-center space-x-3">
          {/* Status Dropdown */}
          <select
            value={candidate.status}
            disabled={isUpdatingStatus}
            onChange={(e) => handleStatusChange(e.target.value as CandidateStatus)}
            className="text-xs font-semibold bg-white border border-slate-300 rounded px-2.5 py-1.5 text-slate-800 focus:ring-1 focus:ring-blue-600 focus:outline-none"
          >
            <option value="NEW">Status: New</option>
            <option value="SCREENED">Status: Screened</option>
            <option value="UNDER_REVIEW">Status: Under Review</option>
            <option value="SHORTLISTED">Status: Shortlisted</option>
            <option value="INTERVIEW">Status: Interview</option>
            <option value="REJECTED">Status: Rejected</option>
            <option value="HIRED">Status: Hired</option>
          </select>

          <button
            onClick={onClose}
            aria-label="Close candidate profile"
            className="p-1.5 rounded-md hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="px-5 border-b border-slate-200 bg-white flex space-x-6 text-xs font-semibold text-slate-500">
        {[
          { id: 'overview', label: 'Evaluation Overview' },
          { id: 'requirements', label: 'Requirements Matrix' },
          { id: 'evidence', label: 'Evidence Quality' },
          { id: 'claims', label: 'AI Claim Audit' },
          { id: 'experience', label: 'Work History' },
          { id: 'notes', label: `Recruiter Notes (${candidate.recruiter_notes?.length || 0})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`py-3 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600 font-bold'
                : 'border-transparent hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Tab Content */}
      <div className="p-5 flex-1 bg-slate-50/50 space-y-5">
        {activeTab === 'overview' && (
          <>
            {/* WHY THIS CANDIDATE Section */}
            <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-blue-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Why This Candidate?
                </h3>
              </div>

              {/* Recommendation Box */}
              <div className="p-3.5 bg-blue-50/60 border border-blue-100 rounded-md">
                <span className="text-[11px] font-bold text-blue-900 uppercase tracking-wider block mb-1">
                  Overall Recommendation
                </span>
                <p className="text-xs text-slate-800 leading-relaxed">
                  {score.summary_justification}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                {/* Strengths */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-emerald-800 flex items-center space-x-1.5 uppercase tracking-wider">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Key Strengths</span>
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-700">
                    {strengths.map((s, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-emerald-600 font-bold">✓</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Gaps */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-amber-800 flex items-center space-x-1.5 uppercase tracking-wider">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    <span>Potential Gaps & Probes</span>
                  </span>
                  {gaps.length > 0 ? (
                    <ul className="space-y-1.5 text-xs text-slate-700">
                      {gaps.map((g, idx) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <span className="text-amber-600 font-bold">⚠</span>
                          <span>{g}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No major qualification gaps identified.</p>
                  )}
                </div>
              </div>
            </div>

            {/* Score Breakdown Progress Bars */}
            <ScoreBreakdown score={score} />

            {/* Requirement Matrix Snippet */}
            <RequirementMatrix matches={score.requirement_matches || []} />
          </>
        )}

        {activeTab === 'requirements' && (
          <RequirementMatrix matches={score.requirement_matches || []} />
        )}

        {activeTab === 'evidence' && (
          <EvidencePanel candidate={candidate} />
        )}

        {activeTab === 'claims' && (
          <ClaimAuditTable claims={score.verified_claims} />
        )}

        {activeTab === 'experience' && (
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Work Experience History
            </h4>
            {candidate.experience.map((exp, idx) => (
              <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="text-sm font-bold text-slate-900">{exp.title}</h5>
                    <span className="text-xs text-slate-500">{exp.company || 'Enterprise Company'}</span>
                  </div>
                  <span className="text-xs font-mono text-slate-500">{exp.start_date || '2020'} – {exp.end_date || 'Present'}</span>
                </div>

                <ul className="space-y-1.5 pt-2 text-xs text-slate-700 list-disc list-inside leading-relaxed">
                  {exp.bullets.map((b, bIdx) => (
                    <li key={bIdx}>{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'notes' && (
          <div className="space-y-4">
            {/* Add Note Form */}
            <form onSubmit={handleAddNote} className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
              <label htmlFor="recruiter-note-text" className="text-xs font-bold text-slate-900 uppercase tracking-wider block">
                Add Recruiter Note / Interview Feedback
              </label>
              <textarea
                id="recruiter-note-text"
                rows={3}
                placeholder="Type internal candidate evaluation notes, interview questions, or follow-up tasks..."
                value={newNoteText}
                onChange={(e) => setNewNoteText(e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-200 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isSubmittingNote || !newNoteText.trim()}
                  className="px-3.5 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Save Note</span>
                </button>
              </div>
            </form>

            {/* Note List */}
            <div className="space-y-2.5">
              {(candidate.recruiter_notes || []).length === 0 ? (
                <p className="text-xs text-slate-500 italic text-center py-6">No recruiter notes recorded yet.</p>
              ) : (
                candidate.recruiter_notes.map((note) => (
                  <div key={note.id} className="p-3 bg-white border border-slate-200 rounded-lg shadow-sm space-y-1">
                    <div className="flex justify-between items-center text-[11px] text-slate-400">
                      <span className="font-semibold text-slate-700">{note.author}</span>
                      <span>{note.timestamp ? new Date(note.timestamp).toLocaleDateString() : 'Recent'}</span>
                    </div>
                    <p className="text-xs text-slate-800">{note.text}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

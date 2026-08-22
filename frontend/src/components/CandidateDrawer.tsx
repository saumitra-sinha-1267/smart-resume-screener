import React, { useEffect, useRef } from 'react';
import {
  X,
  ShieldCheck,
  CheckCircle,
  ExternalLink,
  Bot,
  Scale,
  AlertTriangle
} from 'lucide-react';
import { ScreeningResult } from '../types';

interface CandidateDrawerProps {
  result: ScreeningResult | null;
  anonymized: boolean;
  onClose: () => void;
}

export const CandidateDrawer: React.FC<CandidateDrawerProps> = ({
  result,
  anonymized,
  onClose,
}) => {
  const drawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (result) {
      window.addEventListener('keydown', handleKeyDown);
      drawerRef.current?.focus();
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [result, onClose]);

  if (!result) return null;

  const { candidate, score } = result;
  const displayName = anonymized
    ? candidate.anonymized_name || `Candidate #${candidate.candidate_id.slice(0, 6)}`
    : candidate.raw_name || 'Anonymous Candidate';

  const isLlmScored = score.scoring_method === 'llm';
  const hasFailed = score.flags.some((f) => f.startsWith('scoring_failed'));

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Candidate dossier for ${displayName}`}
      tabIndex={-1}
      ref={drawerRef}
      className="fixed inset-y-0 right-0 w-full max-w-2xl bg-dossier-surface border-l border-dossier-border shadow-2xl z-50 overflow-y-auto p-6 flex flex-col space-y-6 outline-none"
    >
      {/* Dossier Header */}
      <div className="flex items-start justify-between pb-4 border-b border-dossier-border">
        <div>
          <div className="flex items-center space-x-2 font-mono text-xs">
            {hasFailed ? (
              <span className="px-2 py-0.5 rounded bg-dossier-unconfirmedBg border border-dossier-unconfirmed text-dossier-unconfirmed font-bold flex items-center space-x-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>EVALUATION FAILED • NEEDS MANUAL REVIEW</span>
              </span>
            ) : (
              <>
                <span className="px-2 py-0.5 rounded bg-dossier-canvas border border-dossier-amber text-dossier-amber font-bold">
                  DETERMINATION: {score.overall_score.toFixed(1)} / 10
                </span>
                <span className={`px-2 py-0.5 rounded border flex items-center space-x-1 ${
                  isLlmScored
                    ? 'bg-dossier-amberBg text-dossier-amberLight border-dossier-amber/60'
                    : 'bg-dossier-subtle text-slate-300 border-dossier-border'
                }`}>
                  {isLlmScored ? <Bot className="w-3 h-3" /> : <Scale className="w-3 h-3" />}
                  <span>{isLlmScored ? 'LLM-Evaluated' : 'Deterministic Rule Engine'}</span>
                </span>
                <span className="text-slate-400">Conf: <strong>{score.confidence}</strong></span>
              </>
            )}
          </div>

          <div className="mt-2">
            {anonymized ? (
              <div className="flex items-center space-x-2">
                <span className="redaction-mask font-mono text-sm">REDACTED_IDENTITY</span>
                <h2 className="font-serif text-2xl font-black text-dossier-amber">{candidate.anonymized_name}</h2>
              </div>
            ) : (
              <h2 className="font-serif text-2xl font-black text-slate-100">{displayName}</h2>
            )}
            <p className="text-xs font-mono text-slate-400 mt-1">
              Tenure: {candidate.total_experience_years} Years • {candidate.education[0]?.degree || 'Academic Record Masked'}
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          aria-label="Close candidate dossier (Escape)"
          className="p-1.5 rounded bg-dossier-subtle hover:bg-dossier-border text-slate-400 hover:text-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Determination Summary / Failure Alert */}
      <div className={`p-4 rounded border ${
        hasFailed ? 'bg-dossier-unconfirmedBg border-dossier-unconfirmed/60' : 'bg-dossier-canvas border-dossier-border'
      }`}>
        <div className="flex items-center space-x-2 font-mono text-xs text-dossier-amber font-bold uppercase tracking-wider mb-2">
          <span>§</span>
          <span>{hasFailed ? 'Failure Diagnostic' : 'Official Evaluation Determination & Recommendation'}</span>
        </div>
        <p className="text-xs text-slate-200 leading-relaxed font-sans">
          {score.summary_justification}
        </p>
      </div>

      {/* Sub-Dimension Matrix */}
      {!hasFailed && (
        <div>
          <h4 className="font-mono text-xs text-slate-400 uppercase tracking-wider mb-2.5">
            Dimension Scoring Matrix
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="bg-dossier-canvas p-3 rounded border border-dossier-border font-mono">
              <span className="text-[11px] text-slate-400 block">Skills Match</span>
              <span className="text-lg font-bold text-dossier-verified">{score.skills_match.score.toFixed(1)}/10</span>
              <p className="text-[10px] text-slate-500 mt-1">{score.skills_match.matched.length} matched</p>
            </div>

            <div className="bg-dossier-canvas p-3 rounded border border-dossier-border font-mono">
              <span className="text-[11px] text-slate-400 block">Experience</span>
              <span className="text-lg font-bold text-dossier-blue">{score.experience_relevance.score.toFixed(1)}/10</span>
              <p className="text-[10px] text-slate-500 mt-1">{candidate.total_experience_years} yrs verified</p>
            </div>

            <div className="bg-dossier-canvas p-3 rounded border border-dossier-border font-mono">
              <span className="text-[11px] text-slate-400 block">Seniority</span>
              <span className="text-lg font-bold text-slate-100">{score.seniority_alignment.score.toFixed(1)}/10</span>
              <p className="text-[10px] text-slate-500 mt-1">Autonomy match</p>
            </div>

            <div className="bg-dossier-canvas p-3 rounded border border-dossier-border font-mono">
              <span className="text-[11px] text-slate-400 block">Education</span>
              <span className="text-lg font-bold text-dossier-amber">{score.education_fit.score.toFixed(1)}/10</span>
              <p className="text-[10px] text-slate-500 mt-1">Credentials</p>
            </div>
          </div>
        </div>
      )}

      {/* Claim vs Ground Truth Audit */}
      <div className="bg-dossier-canvas rounded p-4 border border-dossier-border space-y-4 font-mono text-xs">
        <h4 className="text-slate-300 font-bold uppercase tracking-wider text-[11px]">
          Skill Taxonomy & Ground Truth Cross-Check
        </h4>

        {/* Matched Claims */}
        <div>
          <span className="text-slate-400 text-[11px] block mb-1.5">Verified Matched Skills ({score.skills_match.matched.length}):</span>
          <div className="flex flex-wrap gap-1.5">
            {score.skills_match.matched.map((sk) => (
              <span key={sk} className="px-2 py-0.5 rounded bg-dossier-verifiedBg text-dossier-verified border border-dossier-verified/40 text-xs font-semibold flex items-center space-x-1">
                <CheckCircle className="w-3 h-3" />
                <span>{sk}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Inferred Skills */}
        {score.skills_match.inferred && score.skills_match.inferred.length > 0 && (
          <div>
            <span className="text-slate-400 text-[11px] block mb-1.5">Inferred from Action Phrases ({score.skills_match.inferred.length}):</span>
            <div className="flex flex-wrap gap-1.5">
              {score.skills_match.inferred.map((sk) => (
                <span key={sk} className="px-2 py-0.5 rounded bg-dossier-blueBg text-dossier-blue border border-dossier-blue/40 text-xs font-semibold flex items-center space-x-1">
                  <span>⮞</span>
                  <span>{sk}</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Unconfirmed / Missing Claims */}
        {score.skills_match.missing.length > 0 && (
          <div>
            <span className="text-slate-400 text-[11px] block mb-1.5">Unconfirmed / Missing Criteria ({score.skills_match.missing.length}):</span>
            <div className="flex flex-wrap gap-1.5">
              {score.skills_match.missing.map((sk) => (
                <span key={sk} className="px-2 py-0.5 rounded bg-dossier-canvas text-dossier-unconfirmed border border-dashed border-dossier-unconfirmed/60 text-xs line-through opacity-85">
                  {sk}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Hallucination Guard Audit Box */}
      <div className={`p-4 rounded border font-mono text-xs ${
        score.hallucination_guard_passed ? 'bg-dossier-canvas border-dossier-border' : 'bg-dossier-unconfirmedBg border-dossier-unconfirmed'
      }`}>
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center space-x-2 font-bold">
            <ShieldCheck className={`w-4 h-4 ${score.hallucination_guard_passed ? 'text-dossier-verified' : 'text-dossier-unconfirmed'}`} />
            <span className="text-slate-200 uppercase">Hallucination Guard Audit</span>
          </div>
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
            score.hallucination_guard_passed ? 'bg-dossier-verifiedBg text-dossier-verified' : 'bg-dossier-unconfirmedBg text-dossier-unconfirmed'
          }`}>
            {score.hallucination_guard_passed ? 'PASSED (0 UNVERIFIED CLAIMS)' : 'CLAIMS PENALIZED'}
          </span>
        </div>
        <p className="text-[11px] text-slate-400 font-sans">
          Ground-truth claim verification engine confirmed matched skills against source resume extractions.
        </p>
      </div>

      {/* Exhibit A: External Links & GitHub Liveness */}
      {candidate.external_links.length > 0 && (
        <div className="bg-dossier-canvas rounded p-4 border border-dossier-border font-mono text-xs">
          <h4 className="text-slate-300 font-bold uppercase tracking-wider text-[11px] mb-2.5">
            Exhibit A: External Link & GitHub Liveness Seals
          </h4>
          <div className="space-y-2">
            {candidate.external_links.map((link, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 rounded bg-dossier-surface border border-dossier-border text-xs">
                <div className="flex items-center space-x-2">
                  <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                  <a href={link.url} target="_blank" rel="noreferrer" className="text-dossier-amber hover:underline">
                    {link.url}
                  </a>
                </div>
                <div className="flex items-center space-x-2">
                  {link.metadata && link.metadata.stars !== undefined && (
                    <span className="text-slate-400 text-[11px]">⭐ {link.metadata.stars}</span>
                  )}
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    link.verified === true
                      ? 'bg-dossier-verifiedBg text-dossier-verified'
                      : link.verified === null
                      ? 'bg-dossier-amberBg text-dossier-amberLight'
                      : 'bg-dossier-unconfirmedBg text-dossier-unconfirmed'
                  }`}>
                    {link.verified === true ? '[✓ HTTP 200 ACTIVE]' : link.verified === null ? '[RATE LIMITED]' : '[UNREACHABLE]'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Exhibit B: Work Experience & Verbatim Metric Quotes */}
      <div className="space-y-3">
        <h4 className="font-mono text-xs text-slate-400 uppercase tracking-wider">
          Exhibit B: Chronological Experience & Metric Quotes
        </h4>
        {candidate.experience.map((exp, idx) => (
          <div key={idx} className="bg-dossier-canvas p-4 rounded border border-dossier-border space-y-2">
            <div className="flex justify-between items-start">
              <div>
                <h5 className="font-serif font-bold text-sm text-slate-100">{exp.title}</h5>
                <span className="text-xs font-mono text-dossier-amber">{exp.company || 'Technology Enterprise'}</span>
              </div>
              <span className="font-mono text-xs text-slate-500">{exp.start_date} – {exp.end_date}</span>
            </div>

            <ul className="space-y-2 pt-1 font-mono text-xs">
              {exp.bullets.map((b, bIdx) => {
                const hasMetric = /\b\d+(?:\.\d+)?%|\b\d+\s*ms|\b\d+[kKmMbB]|\b\$\d+/.test(b);
                return (
                  <li key={bIdx} className={`dossier-quote text-xs leading-relaxed ${hasMetric ? 'text-slate-100 font-medium' : 'text-slate-400'}`}>
                    <span>{b}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

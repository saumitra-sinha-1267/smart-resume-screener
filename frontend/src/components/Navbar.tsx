import React from 'react';
import { Shield, FileCheck, Eye, EyeOff, RotateCcw, Download } from 'lucide-react';

interface NavbarProps {
  anonymized: boolean;
  onToggleAnonymized: () => void;
  onSeedData: () => void;
  onExportCsv: () => void;
  isSeeding: boolean;
  activeJobTitle?: string;
  totalCandidates: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  anonymized,
  onToggleAnonymized,
  onSeedData,
  onExportCsv,
  isSeeding,
  activeJobTitle,
  totalCandidates
}) => {
  return (
    <header className="border-b border-dossier-border bg-dossier-surface/95 backdrop-blur sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Docket Title */}
        <div className="flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded bg-[#161d2c] border border-dossier-amber/60 flex items-center justify-center text-dossier-amber font-mono font-bold text-sm shadow-inner">
            §
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-serif text-lg font-bold text-slate-100 tracking-tight">
                Smart Resume Screener
              </h1>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-dossier-canvas border border-dossier-border text-slate-400">
                CASE DOSSIER ENGINE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans">
              Evidence Extraction • MiniLM Embeddings • Hallucination Audit
            </p>
          </div>
        </div>

        {/* Global Control Stamps */}
        <div className="flex items-center space-x-3">
          
          {/* PII Redaction Switch */}
          <button
            onClick={onToggleAnonymized}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded border text-xs font-mono font-semibold transition-all ${
              anonymized
                ? 'bg-dossier-amberBg border-dossier-amber text-dossier-amberLight hover:brightness-110'
                : 'bg-dossier-subtle border-dossier-border text-slate-300 hover:border-slate-500'
            }`}
            title="Toggle Blind Evaluation: masks candidate identities, graduation years, locations, and contact info"
          >
            {anonymized ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5 text-slate-400" />}
            <span>BLIND REVIEW: <strong>{anonymized ? '[REDACTED]' : '[REVEALED]'}</strong></span>
          </button>

          {/* Seed Sample Resumes */}
          <button
            onClick={onSeedData}
            disabled={isSeeding}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-dossier-subtle hover:bg-dossier-border border border-dossier-border text-xs font-mono font-medium text-slate-300 transition-colors disabled:opacity-50"
            title="Load benchmark candidate case files and preconfigured roles"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isSeeding ? 'animate-spin text-dossier-amber' : 'text-slate-400'}`} />
            <span>{isSeeding ? 'Ingesting...' : 'Seed Benchmarks'}</span>
          </button>

          {/* Export Report CSV */}
          <button
            onClick={onExportCsv}
            disabled={totalCandidates === 0}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-dossier-amber hover:bg-dossier-amberLight text-black font-mono text-xs font-bold transition-all disabled:opacity-50 shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Docket</span>
          </button>
        </div>
      </div>
    </header>
  );
};

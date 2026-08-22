import React from 'react';
import {
  Search,
  Eye,
  EyeOff,
  Download,
  Database,
  Loader2,
  Bell,
  CheckCircle2,
  Menu
} from 'lucide-react';

interface TopbarProps {
  pageTitle: string;
  breadcrumb?: string;
  anonymized: boolean;
  onToggleAnonymized: () => void;
  onSeedData: () => void;
  onExportCsv: () => void;
  isSeeding: boolean;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onOpenMobileMenu?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  pageTitle,
  breadcrumb = 'Overview',
  anonymized,
  onToggleAnonymized,
  onSeedData,
  onExportCsv,
  isSeeding,
  searchQuery,
  onSearchChange,
  onOpenMobileMenu,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between z-20 shrink-0 shadow-sm">
      {/* Page Title & Breadcrumb */}
      <div className="flex items-center space-x-3">
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            aria-label="Open navigation menu"
            className="md:hidden p-2 rounded text-slate-600 hover:bg-slate-100"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <div>
          <div className="text-[11px] font-medium text-slate-400 flex items-center space-x-1.5">
            <span>ATS Portal</span>
            <span>/</span>
            <span className="text-slate-600">{breadcrumb}</span>
          </div>
          <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight leading-tight">
            {pageTitle}
          </h1>
        </div>
      </div>

      {/* Controls & Search */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Global Search */}
        <div className="relative hidden lg:block w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search candidate, skill, title..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-600 focus:bg-white"
          />
        </div>

        {/* Blind Review Redaction Toggle */}
        <button
          onClick={onToggleAnonymized}
          title="Toggle PII Masking"
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border transition-all ${
            anonymized
              ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
              : 'bg-amber-50 text-amber-800 border-amber-300'
          }`}
        >
          {anonymized ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
          <span className="hidden sm:inline">
            {anonymized ? 'Blind Review (Masked)' : 'PII Revealed'}
          </span>
        </button>

        {/* Export CSV */}
        <button
          onClick={onExportCsv}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 shadow-sm transition-colors"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">Export</span>
        </button>

        {/* Seed Benchmark Data */}
        <button
          onClick={onSeedData}
          disabled={isSeeding}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-colors disabled:opacity-50"
        >
          {isSeeding ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
          ) : (
            <Database className="w-3.5 h-3.5 text-blue-600" />
          )}
          <span className="hidden sm:inline">Demo Benchmarks</span>
        </button>

        {/* Notifications */}
        <div className="relative border-l border-slate-200 pl-3 ml-1">
          <button
            aria-label="View notifications"
            className="p-1.5 rounded-md text-slate-500 hover:text-slate-700 hover:bg-slate-100 relative"
          >
            <Bell className="w-4 h-4" />
            <span className="w-2 h-2 rounded-full bg-blue-600 absolute top-1 right-1" />
          </button>
        </div>
      </div>
    </header>
  );
};

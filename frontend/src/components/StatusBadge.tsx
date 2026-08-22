import React from 'react';
import { CandidateStatus } from '../types';

interface StatusBadgeProps {
  status: CandidateStatus | string;
  size?: 'sm' | 'md';
}

const statusConfig: Record<string, { label: string; bg: string; text: string; border: string }> = {
  NEW: { label: 'New', bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200' },
  SCREENED: { label: 'Screened', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  UNDER_REVIEW: { label: 'Under Review', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  SHORTLISTED: { label: 'Shortlisted', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  INTERVIEW: { label: 'Interview', bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  REJECTED: { label: 'Rejected', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  HIRED: { label: 'Hired', bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'sm' }) => {
  const config = statusConfig[status] || {
    label: status,
    bg: 'bg-slate-100',
    text: 'text-slate-600',
    border: 'border-slate-200',
  };

  const pad = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center font-medium rounded border ${config.bg} ${config.text} ${config.border} ${pad}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-70" />
      {config.label}
    </span>
  );
};

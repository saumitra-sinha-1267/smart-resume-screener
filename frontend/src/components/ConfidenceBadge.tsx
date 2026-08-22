import React from 'react';

interface ConfidenceBadgeProps {
  confidence: 'High' | 'Medium' | 'Low' | string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  if (confidence === 'High') {
    return (
      <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5" />
        High Conf.
      </span>
    );
  } else if (confidence === 'Medium') {
    return (
      <span className="inline-flex items-center text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5" />
        Med Conf.
      </span>
    );
  }
  return (
    <span className="inline-flex items-center text-[11px] font-semibold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded">
      <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5" />
      Low Conf.
    </span>
  );
};

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { StatusBadge } from '../components/StatusBadge';
import { ConfidenceBadge } from '../components/ConfidenceBadge';
import { KpiCard } from '../components/KpiCard';
import { Users } from 'lucide-react';

describe('Enterprise UI Components', () => {
  it('renders status badges properly', () => {
    render(<StatusBadge status="SHORTLISTED" />);
    expect(screen.getByText('Shortlisted')).toBeDefined();
  });

  it('renders confidence badge with high level', () => {
    render(<ConfidenceBadge confidence="High" />);
    expect(screen.getByText('High Conf.')).toBeDefined();
  });

  it('renders KPI card with real metric', () => {
    render(
      <KpiCard
        title="TOTAL CANDIDATES"
        value={42}
        subtitle="Test subtitle"
        icon={Users}
      />
    );
    expect(screen.getByText('TOTAL CANDIDATES')).toBeDefined();
    expect(screen.getByText('42')).toBeDefined();
    expect(screen.getByText('Test subtitle')).toBeDefined();
  });
});

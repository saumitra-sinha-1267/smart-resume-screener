import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { JobModal } from '../components/JobModal';
import * as api from '../services/api';

describe('JobModal Component', () => {
  it('renders input elements and Extract Requirements button', () => {
    render(<JobModal isOpen={true} onClose={() => {}} onJobCreated={() => {}} />);
    expect(screen.getByText('Create Job Position')).toBeDefined();
    expect(screen.getByPlaceholderText(/Paste the complete raw job description/i)).toBeDefined();
    expect(screen.getByRole('button', { name: /Extract Requirements/i })).toBeDefined();
  });

  it('handles empty JD extraction with recruiter-friendly message', async () => {
    render(<JobModal isOpen={true} onClose={() => {}} onJobCreated={() => {}} />);
    const extractBtn = screen.getByRole('button', { name: /Extract Requirements/i });
    // Initially disabled if textarea is empty
    expect((extractBtn as HTMLButtonElement).disabled).toBe(true);
  });

  it('extracts requirements and populates fields when API succeeds', async () => {
    const mockParsedJob = {
      job_id: 'job-123',
      title: 'Data Analyst – Fresher',
      department: 'Data & Analytics',
      seniority: 'Entry-Level',
      min_experience_years: 0,
      required_skills: ['Python', 'SQL', 'Pandas', 'NumPy', 'Statistics', 'Data Visualization'],
      preferred_skills: ['Power BI', 'Microsoft Excel', 'Tableau', 'Git / GitHub'],
      education_requirements: ["Bachelor's in Computer Science or Statistics"],
      certifications: [],
      domain_requirements: [],
      responsibilities: [],
      mandatory_requirements: ['Expertise in Python', 'Expertise in SQL'],
      preferred_requirements: ['Familiarity with Power BI'],
      requirements: [],
      raw_description: 'Test Fresher Data Analyst JD',
    };

    vi.spyOn(api, 'parseJobDescription').mockResolvedValueOnce(mockParsedJob as any);

    render(<JobModal isOpen={true} onClose={() => {}} onJobCreated={() => {}} />);
    const textarea = screen.getByPlaceholderText(/Paste the complete raw job description/i);
    fireEvent.change(textarea, { target: { value: 'Test Fresher Data Analyst JD' } });

    const extractBtn = screen.getByRole('button', { name: /Extract Requirements/i });
    expect((extractBtn as HTMLButtonElement).disabled).toBe(false);

    fireEvent.click(extractBtn);

    await waitFor(() => {
      expect(screen.getByText('Extracted Requirements')).toBeDefined();
      expect(screen.getByText('Python')).toBeDefined();
      expect(screen.getByText('SQL')).toBeDefined();
      expect(screen.getByText('Power BI')).toBeDefined();
    });
  });

  it('displays friendly error message when extraction fails', async () => {
    vi.spyOn(api, 'parseJobDescription').mockRejectedValueOnce(new Error('Network error'));

    render(<JobModal isOpen={true} onClose={() => {}} onJobCreated={() => {}} />);
    const textarea = screen.getByPlaceholderText(/Paste the complete raw job description/i);
    fireEvent.change(textarea, { target: { value: 'Some job description text' } });

    const extractBtn = screen.getByRole('button', { name: /Extract Requirements/i });
    fireEvent.click(extractBtn);

    await waitFor(() => {
      expect(screen.getByText(/Unable to extract requirements/i)).toBeDefined();
    });
  });
});

import React, { useState } from 'react';
import { Briefcase, Plus, ChevronDown, Loader2 } from 'lucide-react';
import { JobData } from '../types';

interface JobSelectorProps {
  jobs: JobData[];
  selectedJob: JobData | null;
  isLoadingJobs?: boolean;
  onSelectJob: (job: JobData) => void;
  onCreateJob: (job: Partial<JobData>) => void;
}

export const JobSelector: React.FC<JobSelectorProps> = ({
  jobs,
  selectedJob,
  isLoadingJobs = false,
  onSelectJob,
  onCreateJob,
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDepartment, setNewDepartment] = useState('Engineering');
  const [newMinExp, setNewMinExp] = useState(4);
  const [newReqSkills, setNewReqSkills] = useState('');
  const [newDescription, setNewDescription] = useState('');

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDescription.trim()) return;

    const skillsArray = newReqSkills
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    onCreateJob({
      title: newTitle,
      department: newDepartment,
      min_experience_years: Number(newMinExp),
      required_skills: skillsArray,
      preferred_skills: [],
      raw_description: newDescription,
      requirements: skillsArray.map((s) => ({
        id: Math.random().toString(),
        text: `Demonstrated expertise in ${s}`,
        category: 'skill',
        weight: 1.0,
        required: true,
      })),
    });

    setIsCreating(false);
    setNewTitle('');
    setNewDescription('');
    setNewReqSkills('');
  };

  return (
    <div className="bg-dossier-surface border border-dossier-border rounded-lg p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-dossier-border">
        <div>
          <div className="flex items-center space-x-2 text-dossier-amber font-mono text-xs uppercase tracking-wider font-semibold">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Active Position Under Evaluation</span>
          </div>
          <h2 className="font-serif text-2xl font-bold text-slate-100 mt-1 flex items-center space-x-2">
            {isLoadingJobs ? (
              <span className="flex items-center space-x-2 text-slate-400 text-lg">
                <Loader2 className="w-4 h-4 animate-spin text-dossier-amber" />
                <span>Loading available roles...</span>
              </span>
            ) : selectedJob ? (
              <span>{selectedJob.title}</span>
            ) : (
              <span className="text-slate-400">Select Target Role</span>
            )}
          </h2>
        </div>

        <div className="flex items-center space-x-2">
          {/* Target Role Dropdown */}
          <div className="relative">
            <select
              aria-label="Select Target Position"
              disabled={isLoadingJobs || jobs.length === 0}
              value={selectedJob?.job_id || ''}
              onChange={(e) => {
                const found = jobs.find((j) => j.job_id === e.target.value);
                if (found) onSelectJob(found);
              }}
              className="appearance-none bg-dossier-subtle text-slate-200 border border-dossier-border text-xs font-mono font-medium rounded px-3 py-2 pr-8 focus:outline-none focus:border-dossier-amber cursor-pointer disabled:opacity-50"
            >
              {isLoadingJobs ? (
                <option value="">Loading positions...</option>
              ) : jobs.length === 0 ? (
                <option value="">No roles defined yet</option>
              ) : (
                jobs.map((j) => (
                  <option key={j.job_id} value={j.job_id}>
                    {j.title} [{j.min_experience_years}+ yrs]
                  </option>
                ))
              )}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
          </div>

          <button
            onClick={() => setIsCreating(!isCreating)}
            aria-label="Create New Position"
            className="flex items-center space-x-1 px-3 py-2 rounded bg-dossier-subtle hover:bg-dossier-border border border-dossier-border text-slate-300 text-xs font-mono font-semibold transition-all"
          >
            <Plus className="w-3.5 h-3.5 text-dossier-amber" />
            <span>New Role</span>
          </button>
        </div>
      </div>

      {/* Selected Job Exhibits */}
      {selectedJob && !isCreating && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-dossier-canvas p-3 rounded border border-dossier-border">
            <span className="text-slate-400 font-mono text-[11px] block mb-1.5 uppercase">Mandatory Skill Rubric:</span>
            <div className="flex flex-wrap gap-1.5">
              {selectedJob.required_skills.map((sk) => (
                <span
                  key={sk}
                  className="font-mono text-[11px] px-2 py-0.5 rounded bg-dossier-subtle text-slate-200 border border-dossier-border"
                >
                  {sk}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-dossier-canvas p-3 rounded border border-dossier-border font-mono">
            <span className="text-slate-400 text-[11px] block mb-1 uppercase">Department & Experience:</span>
            <p className="text-slate-200 font-semibold text-xs">
              {selectedJob.department || 'Engineering'} • {selectedJob.min_experience_years}+ Years Minimum
            </p>
          </div>

          <div className="bg-dossier-canvas p-3 rounded border border-dossier-border font-mono">
            <span className="text-slate-400 text-[11px] block mb-1 uppercase">Evaluation Parameters:</span>
            <p className="text-slate-200 font-semibold text-xs">
              {selectedJob.requirements.length} Criteria • MiniLM Dense Semantic Index
            </p>
          </div>
        </div>
      )}

      {/* Define Custom Role Form */}
      {isCreating && (
        <form onSubmit={handleCreateSubmit} className="mt-4 bg-dossier-canvas p-4 rounded border border-dossier-border space-y-3">
          <h3 className="font-serif text-sm font-bold text-slate-200">Define Custom Job Description</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label htmlFor="new-job-title" className="text-[11px] font-mono text-slate-400 block mb-1">Job Title</label>
              <input
                id="new-job-title"
                type="text"
                placeholder="e.g. Senior Machine Learning Engineer"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                required
                className="w-full bg-dossier-subtle border border-dossier-border text-xs font-mono rounded px-3 py-1.5 text-slate-100 focus:outline-none focus:border-dossier-amber"
              />
            </div>
            <div>
              <label htmlFor="new-job-dept" className="text-[11px] font-mono text-slate-400 block mb-1">Department</label>
              <input
                id="new-job-dept"
                type="text"
                value={newDepartment}
                onChange={(e) => setNewDepartment(e.target.value)}
                className="w-full bg-dossier-subtle border border-dossier-border text-xs font-mono rounded px-3 py-1.5 text-slate-100 focus:outline-none focus:border-dossier-amber"
              />
            </div>
            <div>
              <label htmlFor="new-job-exp" className="text-[11px] font-mono text-slate-400 block mb-1">Min Experience (Years)</label>
              <input
                id="new-job-exp"
                type="number"
                value={newMinExp}
                onChange={(e) => setNewMinExp(Number(e.target.value))}
                min={0}
                className="w-full bg-dossier-subtle border border-dossier-border text-xs font-mono rounded px-3 py-1.5 text-slate-100 focus:outline-none focus:border-dossier-amber"
              />
            </div>
          </div>

          <div>
            <label htmlFor="new-job-skills" className="text-[11px] font-mono text-slate-400 block mb-1">Required Skills (Comma-separated)</label>
            <input
              id="new-job-skills"
              type="text"
              placeholder="Python, PyTorch, Kubernetes, FastAPI, PostgreSQL"
              value={newReqSkills}
              onChange={(e) => setNewReqSkills(e.target.value)}
              className="w-full bg-dossier-subtle border border-dossier-border text-xs font-mono rounded px-3 py-1.5 text-slate-100 focus:outline-none focus:border-dossier-amber"
            />
          </div>

          <div>
            <label htmlFor="new-job-desc" className="text-[11px] font-mono text-slate-400 block mb-1">Full Job Description Text</label>
            <textarea
              id="new-job-desc"
              rows={3}
              placeholder="Paste responsibilities, qualifications, and stack requirements..."
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              required
              className="w-full bg-dossier-subtle border border-dossier-border text-xs font-mono rounded px-3 py-1.5 text-slate-100 focus:outline-none focus:border-dossier-amber"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="px-3 py-1.5 rounded bg-dossier-subtle text-slate-300 text-xs font-mono"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded bg-dossier-amber hover:bg-dossier-amberLight text-black text-xs font-mono font-bold"
            >
              Record Position
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

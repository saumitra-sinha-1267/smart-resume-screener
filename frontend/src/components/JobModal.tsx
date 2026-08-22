import React, { useState } from 'react';
import { X, Sparkles, Loader2, Plus, Check } from 'lucide-react';
import { JobData } from '../types';
import { createJob, parseJobDescription } from '../services/api';

interface JobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJobCreated: (job: JobData) => void;
}

export const JobModal: React.FC<JobModalProps> = ({ isOpen, onClose, onJobCreated }) => {
  const [rawDescription, setRawDescription] = useState('');
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('Engineering');
  const [seniority, setSeniority] = useState('Senior');
  const [minExp, setMinExp] = useState(4);
  const [requiredSkills, setRequiredSkills] = useState<string[]>(['Python', 'FastAPI', 'PostgreSQL']);
  const [preferredSkills, setPreferredSkills] = useState<string[]>(['Docker', 'Kubernetes']);
  const [newSkillInput, setNewSkillInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const handleAnalyze = async () => {
    if (!rawDescription.trim()) return;
    try {
      setIsAnalyzing(true);
      const parsed = await parseJobDescription(rawDescription, title);
      setTitle(parsed.title);
      setDepartment(parsed.department || 'Engineering');
      setSeniority(parsed.seniority || 'Senior');
      setMinExp(parsed.min_experience_years || 4);
      if (parsed.required_skills.length > 0) setRequiredSkills(parsed.required_skills);
      if (parsed.preferred_skills.length > 0) setPreferredSkills(parsed.preferred_skills);
    } catch (e: any) {
      alert(`JD Analysis failed: ${e.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAddSkill = (type: 'req' | 'pref') => {
    if (!newSkillInput.trim()) return;
    if (type === 'req') {
      if (!requiredSkills.includes(newSkillInput.trim())) {
        setRequiredSkills([...requiredSkills, newSkillInput.trim()]);
      }
    } else {
      if (!preferredSkills.includes(newSkillInput.trim())) {
        setPreferredSkills([...preferredSkills, newSkillInput.trim()]);
      }
    }
    setNewSkillInput('');
  };

  const handleRemoveSkill = (skill: string, type: 'req' | 'pref') => {
    if (type === 'req') {
      setRequiredSkills(requiredSkills.filter((s) => s !== skill));
    } else {
      setPreferredSkills(preferredSkills.filter((s) => s !== skill));
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      setIsSaving(true);
      const job = await createJob({
        title,
        department,
        seniority,
        min_experience_years: Number(minExp),
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        raw_description: rawDescription || `${title} in ${department}`,
      });
      onJobCreated(job);
      onClose();
    } catch (e: any) {
      alert(`Job creation failed: ${e.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Define Job Position</h3>
            <p className="text-xs text-slate-500">Configure target role requirements or auto-extract with AI</p>
          </div>
          <button onClick={onClose} aria-label="Close modal" className="p-1 rounded text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} className="p-5 overflow-y-auto space-y-4 flex-1 text-xs">
          {/* Raw JD Input with Auto-Analyze */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label htmlFor="job-raw-desc" className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
                Paste Raw Job Description (Optional)
              </label>
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={isAnalyzing || !rawDescription.trim()}
                className="px-2.5 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold flex items-center space-x-1 disabled:opacity-40"
              >
                {isAnalyzing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                <span>Analyze Job Description</span>
              </button>
            </div>
            <textarea
              id="job-raw-desc"
              rows={3}
              placeholder="Paste responsibilities, qualifications, and requirements..."
              value={rawDescription}
              onChange={(e) => setRawDescription(e.target.value)}
              className="w-full p-2.5 border border-slate-200 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none"
            />
          </div>

          {/* Title, Department, Seniority */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label htmlFor="job-title" className="font-semibold text-slate-700 block mb-1">Job Title *</label>
              <input
                id="job-title"
                type="text"
                required
                placeholder="e.g. Staff Backend Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full p-2 border border-slate-200 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="job-dept" className="font-semibold text-slate-700 block mb-1">Department</label>
              <input
                id="job-dept"
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full p-2 border border-slate-200 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="job-exp" className="font-semibold text-slate-700 block mb-1">Min Experience (Yrs)</label>
              <input
                id="job-exp"
                type="number"
                min={0}
                value={minExp}
                onChange={(e) => setMinExp(Number(e.target.value))}
                className="w-full p-2 border border-slate-200 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none"
              />
            </div>
          </div>

          {/* Mandatory Skills */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 uppercase tracking-wider text-[11px] block">
              Mandatory Required Skills
            </label>
            <div className="flex flex-wrap gap-1.5 p-2 bg-slate-50 border border-slate-200 rounded-md min-h-[42px]">
              {requiredSkills.map((s) => (
                <span key={s} className="inline-flex items-center px-2 py-0.5 rounded bg-white text-slate-800 border border-slate-300 text-xs">
                  <span>{s}</span>
                  <button type="button" onClick={() => handleRemoveSkill(s, 'req')} className="ml-1 text-slate-400 hover:text-rose-600">×</button>
                </span>
              ))}
            </div>
          </div>

          {/* Preferred Skills */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-700 uppercase tracking-wider text-[11px] block">
              Preferred Skills / Bonus
            </label>
            <div className="flex flex-wrap gap-1.5 p-2 bg-slate-50 border border-slate-200 rounded-md min-h-[42px]">
              {preferredSkills.map((s) => (
                <span key={s} className="inline-flex items-center px-2 py-0.5 rounded bg-white text-slate-800 border border-slate-300 text-xs">
                  <span>{s}</span>
                  <button type="button" onClick={() => handleRemoveSkill(s, 'pref')} className="ml-1 text-slate-400 hover:text-rose-600">×</button>
                </span>
              ))}
            </div>
          </div>

          {/* Add skill input */}
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Add skill tag..."
              value={newSkillInput}
              onChange={(e) => setNewSkillInput(e.target.value)}
              className="flex-1 p-2 border border-slate-200 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none"
            />
            <button
              type="button"
              onClick={() => handleAddSkill('req')}
              className="px-3 py-1.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs"
            >
              + Mandatory
            </button>
            <button
              type="button"
              onClick={() => handleAddSkill('pref')}
              className="px-3 py-1.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs"
            >
              + Preferred
            </button>
          </div>

          {/* Modal Footer */}
          <div className="pt-3 border-t border-slate-200 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center space-x-1.5 disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
              <span>Save Position</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

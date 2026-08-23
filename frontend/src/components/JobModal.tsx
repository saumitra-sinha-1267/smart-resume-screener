import React, { useState } from 'react';
import { X, FileText, Loader2, Check, ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react';
import { JobData, JobRequirement } from '../types';
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
  const [seniority, setSeniority] = useState('Mid-Level');
  const [minExp, setMinExp] = useState<number>(0);
  const [requiredSkills, setRequiredSkills] = useState<string[]>([]);
  const [preferredSkills, setPreferredSkills] = useState<string[]>([]);
  const [educationRequirements, setEducationRequirements] = useState<string[]>([]);
  const [certifications, setCertifications] = useState<string[]>([]);
  const [domainRequirements, setDomainRequirements] = useState<string[]>([]);
  const [responsibilities, setResponsibilities] = useState<string[]>([]);
  
  const [newSkillInput, setNewSkillInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasExtracted, setHasExtracted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleExtract = async () => {
    if (!rawDescription.trim()) {
      setErrorMessage('Please paste a job description before extracting requirements.');
      return;
    }

    try {
      setIsAnalyzing(true);
      setErrorMessage(null);
      const parsed = await parseJobDescription(rawDescription, title.trim() || undefined);
      
      setTitle(parsed.title || title || 'Untitled Role');
      setDepartment(parsed.department || 'Engineering');
      setSeniority(parsed.seniority || 'Mid-Level');
      setMinExp(parsed.min_experience_years !== undefined ? parsed.min_experience_years : 0);
      setRequiredSkills(parsed.required_skills || []);
      setPreferredSkills(parsed.preferred_skills || []);
      setEducationRequirements(parsed.education_requirements || []);
      setCertifications(parsed.certifications || []);
      setDomainRequirements(parsed.domain_requirements || []);
      setResponsibilities(parsed.responsibilities || []);
      setHasExtracted(true);
    } catch (e: any) {
      setErrorMessage('Unable to extract requirements. Please check the job description and try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAddSkill = (type: 'req' | 'pref') => {
    const trimmed = newSkillInput.trim();
    if (!trimmed) return;

    if (type === 'req') {
      if (!requiredSkills.includes(trimmed)) {
        setRequiredSkills([...requiredSkills, trimmed]);
      }
      setPreferredSkills(preferredSkills.filter((s) => s.toLowerCase() !== trimmed.toLowerCase()));
    } else {
      if (!preferredSkills.includes(trimmed)) {
        setPreferredSkills([...preferredSkills, trimmed]);
      }
      setRequiredSkills(requiredSkills.filter((s) => s.toLowerCase() !== trimmed.toLowerCase()));
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

  const handleMoveSkill = (skill: string, from: 'req' | 'pref') => {
    if (from === 'req') {
      setRequiredSkills(requiredSkills.filter((s) => s !== skill));
      if (!preferredSkills.includes(skill)) {
        setPreferredSkills([...preferredSkills, skill]);
      }
    } else {
      setPreferredSkills(preferredSkills.filter((s) => s !== skill));
      if (!requiredSkills.includes(skill)) {
        setRequiredSkills([...requiredSkills, skill]);
      }
    }
  };

  const handleRemoveEducation = (edu: string) => {
    setEducationRequirements(educationRequirements.filter((e) => e !== edu));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMessage('Please enter a job title.');
      return;
    }

    try {
      setIsSaving(true);
      setErrorMessage(null);

      // Build structured requirements list matching the final edited state
      const finalRequirements: JobRequirement[] = [];

      // Experience requirement
      if (Number(minExp) === 0) {
        finalRequirements.push({
          id: `req-exp-${Date.now()}`,
          text: 'Entry level / 0+ years professional experience',
          category: 'experience',
          weight: 0.5,
          required: false,
          is_mandatory: false,
        });
      } else {
        finalRequirements.push({
          id: `req-exp-${Date.now()}`,
          text: `${minExp}+ years of professional experience`,
          category: 'experience',
          weight: 1.5,
          required: true,
          is_mandatory: true,
        });
      }

      // Mandatory skills
      requiredSkills.forEach((s, idx) => {
        finalRequirements.push({
          id: `req-skill-${idx}-${Date.now()}`,
          text: `Demonstrated hands-on expertise with ${s}`,
          category: 'skill',
          weight: 1.0,
          required: true,
          is_mandatory: true,
        });
      });

      // Preferred skills
      preferredSkills.forEach((p, idx) => {
        finalRequirements.push({
          id: `req-pref-${idx}-${Date.now()}`,
          text: `Experience or familiarity with ${p}`,
          category: 'skill',
          weight: 0.5,
          required: false,
          is_mandatory: false,
        });
      });

      // Education requirements
      educationRequirements.forEach((edu, idx) => {
        finalRequirements.push({
          id: `req-edu-${idx}-${Date.now()}`,
          text: `Academic credential or equivalent: ${edu}`,
          category: 'education',
          weight: 0.7,
          required: false,
          is_mandatory: false,
        });
      });

      const jobPayload: Partial<JobData> = {
        title: title.trim(),
        department: department.trim() || 'Engineering',
        seniority,
        min_experience_years: Number(minExp),
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        education_requirements: educationRequirements,
        certifications,
        domain_requirements: domainRequirements,
        responsibilities,
        mandatory_requirements: requiredSkills.map((s) => `Expertise in ${s}`),
        preferred_requirements: preferredSkills.map((s) => `Familiarity with ${s}`),
        requirements: finalRequirements,
        raw_description: rawDescription || `${title} in ${department}`,
      };

      const savedJob = await createJob(jobPayload);
      onJobCreated(savedJob);
      onClose();
    } catch (e: any) {
      setErrorMessage(e.message || 'Job creation failed. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div>
            <h3 id="modal-title" className="text-sm font-bold text-slate-900">
              Create Job Position
            </h3>
            <p className="text-xs text-slate-500">
              Extract structured requirements from raw job descriptions and review criteria before saving
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="p-1 rounded text-slate-400 hover:text-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} className="p-5 overflow-y-auto space-y-5 flex-1 text-xs">
          {/* Error Banner */}
          {errorMessage && (
            <div
              role="alert"
              className="p-3 bg-rose-50 border border-rose-200 rounded-md text-rose-800 text-xs flex items-center space-x-2"
            >
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Section 1: Job Description Input & Extraction */}
          <div className="space-y-3 bg-slate-50/80 p-3.5 border border-slate-200 rounded-lg">
            <div>
              <label
                htmlFor="job-title-input"
                className="font-bold text-slate-700 uppercase tracking-wider text-[11px] block mb-1"
              >
                Job Title
              </label>
              <input
                id="job-title-input"
                type="text"
                placeholder="e.g. Data Analyst – Fresher"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full p-2 border border-slate-300 rounded-md bg-white focus:ring-1 focus:ring-blue-600 focus:outline-none text-xs text-slate-800"
              />
            </div>

            <div>
              <label
                htmlFor="job-raw-desc"
                className="font-bold text-slate-700 uppercase tracking-wider text-[11px] block mb-1"
              >
                Job Description
              </label>
              <textarea
                id="job-raw-desc"
                rows={5}
                placeholder="Paste the complete raw job description here (responsibilities, required qualifications, preferred skills, education)..."
                value={rawDescription}
                onChange={(e) => setRawDescription(e.target.value)}
                className="w-full p-2.5 border border-slate-300 rounded-md bg-white focus:ring-1 focus:ring-blue-600 focus:outline-none font-mono text-xs text-slate-800"
              />
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleExtract}
                disabled={isAnalyzing || !rawDescription.trim()}
                className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50 transition-colors shadow-sm cursor-pointer"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Extracting requirements...</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-3.5 h-3.5" />
                    <span>Extract Requirements</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Section 2: Extracted Requirements (Editable) */}
          {(hasExtracted || requiredSkills.length > 0 || preferredSkills.length > 0 || title) && (
            <div className="space-y-4 pt-2 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                    Extracted Requirements
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    Review and edit the structured criteria that will be used for screening candidates
                  </p>
                </div>
                {hasExtracted && (
                  <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-semibold flex items-center space-x-1">
                    <Check className="w-3 h-3" />
                    <span>Parsed from JD</span>
                  </span>
                )}
              </div>

              {/* Role Details Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-white p-3 border border-slate-200 rounded-lg">
                <div>
                  <label htmlFor="edit-dept" className="font-semibold text-slate-700 block mb-1 text-[11px]">
                    Department
                  </label>
                  <input
                    id="edit-dept"
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full p-1.5 border border-slate-200 rounded focus:ring-1 focus:ring-blue-600 focus:outline-none text-xs"
                  />
                </div>

                <div>
                  <label htmlFor="edit-seniority" className="font-semibold text-slate-700 block mb-1 text-[11px]">
                    Seniority
                  </label>
                  <select
                    id="edit-seniority"
                    value={seniority}
                    onChange={(e) => setSeniority(e.target.value)}
                    className="w-full p-1.5 border border-slate-200 rounded bg-white focus:ring-1 focus:ring-blue-600 focus:outline-none text-xs"
                  >
                    <option value="Entry-Level">Entry-Level (Fresher / Intern)</option>
                    <option value="Junior">Junior</option>
                    <option value="Associate">Associate</option>
                    <option value="Mid-Level">Mid-Level</option>
                    <option value="Senior">Senior</option>
                    <option value="Lead">Lead</option>
                    <option value="Staff">Staff</option>
                    <option value="Principal">Principal</option>
                    <option value="Manager">Manager</option>
                    <option value="Director">Director</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="edit-min-exp" className="font-semibold text-slate-700 block mb-1 text-[11px]">
                    Min Experience (Years)
                  </label>
                  <input
                    id="edit-min-exp"
                    type="number"
                    min={0}
                    step={0.5}
                    value={minExp}
                    onChange={(e) => setMinExp(Number(e.target.value))}
                    className="w-full p-1.5 border border-slate-200 rounded focus:ring-1 focus:ring-blue-600 focus:outline-none text-xs"
                  />
                </div>

                <div>
                  <span className="font-semibold text-slate-700 block mb-1 text-[11px]">Experience Type</span>
                  <div className="p-1.5 text-xs text-slate-600 font-medium">
                    {minExp === 0 ? (
                      <span className="text-emerald-700 font-semibold">0+ Years (Fresher)</span>
                    ) : (
                      <span>{minExp}+ Years Minimum</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Required Skills (Mandatory) */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="font-bold text-slate-800 uppercase tracking-wider text-[11px] flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
                    <span>Required Skills (Mandatory Gating)</span>
                  </label>
                  <span className="text-[10px] text-slate-500">{requiredSkills.length} mandatory skill(s)</span>
                </div>
                <div className="flex flex-wrap gap-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-md min-h-[46px]">
                  {requiredSkills.length === 0 ? (
                    <span className="text-slate-400 text-xs italic py-0.5">No mandatory skills configured.</span>
                  ) : (
                    requiredSkills.map((s) => (
                      <span
                        key={s}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-white text-slate-800 border border-slate-300 text-xs shadow-xs"
                      >
                        <span className="font-medium">{s}</span>
                        <button
                          type="button"
                          title="Move to Preferred"
                          onClick={() => handleMoveSkill(s, 'req')}
                          className="p-0.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <ArrowRight className="w-3 h-3" />
                        </button>
                        <button
                          type="button"
                          title="Remove Skill"
                          onClick={() => handleRemoveSkill(s, 'req')}
                          className="p-0.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded font-bold"
                        >
                          ×
                        </button>
                      </span>
                    ))
                  )}
                </div>
              </div>

              {/* Preferred Skills (Bonus) */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="font-bold text-slate-800 uppercase tracking-wider text-[11px] flex items-center space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
                    <span>Preferred Skills (Bonus Criteria)</span>
                  </label>
                  <span className="text-[10px] text-slate-500">{preferredSkills.length} preferred skill(s)</span>
                </div>
                <div className="flex flex-wrap gap-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-md min-h-[46px]">
                  {preferredSkills.length === 0 ? (
                    <span className="text-slate-400 text-xs italic py-0.5">No preferred skills configured.</span>
                  ) : (
                    preferredSkills.map((s) => (
                      <span
                        key={s}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-white text-slate-800 border border-slate-300 text-xs shadow-xs"
                      >
                        <button
                          type="button"
                          title="Move to Required"
                          onClick={() => handleMoveSkill(s, 'pref')}
                          className="p-0.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded"
                        >
                          <ArrowLeft className="w-3 h-3" />
                        </button>
                        <span className="font-medium">{s}</span>
                        <button
                          type="button"
                          title="Remove Skill"
                          onClick={() => handleRemoveSkill(s, 'pref')}
                          className="p-0.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded font-bold"
                        >
                          ×
                        </button>
                      </span>
                    ))
                  )}
                </div>
              </div>

              {/* Add Custom Skill Row */}
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="Type a skill name (e.g. PyTorch, Docker, Tableau)..."
                  value={newSkillInput}
                  onChange={(e) => setNewSkillInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddSkill('req');
                    }
                  }}
                  className="flex-1 p-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-blue-600 focus:outline-none text-xs"
                />
                <button
                  type="button"
                  onClick={() => handleAddSkill('req')}
                  disabled={!newSkillInput.trim()}
                  className="px-3 py-1.5 rounded bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-semibold text-xs disabled:opacity-40 cursor-pointer"
                >
                  + Add Required
                </button>
                <button
                  type="button"
                  onClick={() => handleAddSkill('pref')}
                  disabled={!newSkillInput.trim()}
                  className="px-3 py-1.5 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-semibold text-xs disabled:opacity-40 cursor-pointer"
                >
                  + Add Preferred
                </button>
              </div>

              {/* Other Structured Requirements (Education, Domain, Certs) */}
              {(educationRequirements.length > 0 ||
                domainRequirements.length > 0 ||
                certifications.length > 0 ||
                responsibilities.length > 0) && (
                <div className="space-y-3 pt-2 border-t border-slate-200">
                  <h5 className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
                    Other Requirements
                  </h5>

                  {educationRequirements.length > 0 && (
                    <div>
                      <span className="text-[11px] font-semibold text-slate-600 block mb-1">
                        Education Requirements:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {educationRequirements.map((edu) => (
                          <span
                            key={edu}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 text-xs"
                          >
                            <span>{edu}</span>
                            <button
                              type="button"
                              onClick={() => handleRemoveEducation(edu)}
                              className="text-slate-400 hover:text-rose-600"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {domainRequirements.length > 0 && (
                    <div>
                      <span className="text-[11px] font-semibold text-slate-600 block mb-1">
                        Domain Experience:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {domainRequirements.map((d) => (
                          <span
                            key={d}
                            className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 text-xs"
                          >
                            {d}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {certifications.length > 0 && (
                    <div>
                      <span className="text-[11px] font-semibold text-slate-600 block mb-1">
                        Certifications:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {certifications.map((c) => (
                          <span
                            key={c}
                            className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 text-xs"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Modal Footer */}
          <div className="pt-4 border-t border-slate-200 flex justify-end space-x-2 bg-white sticky bottom-0">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving || !title.trim()}
              className="px-5 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center space-x-1.5 disabled:opacity-50 transition-colors shadow-sm cursor-pointer"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Saving Job...</span>
                </>
              ) : (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Create Job</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
export default JobModal;

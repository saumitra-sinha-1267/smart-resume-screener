import React, { useState, useRef } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { CandidateData } from '../types';
import { uploadResumes } from '../services/api';

interface ResumeUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (candidates: CandidateData[]) => void;
}

export const ResumeUploadModal: React.FC<ResumeUploadModalProps> = ({
  isOpen,
  onClose,
  onUploadSuccess,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      // Validate extensions
      const invalid = files.filter(
        (f) => !f.name.toLowerCase().endsWith('.pdf') && !f.name.toLowerCase().endsWith('.txt')
      );
      if (invalid.length > 0) {
        setError('Only PDF (.pdf) and Plain Text (.txt) files are supported.');
        return;
      }
      // Validate 10MB
      const tooLarge = files.filter((f) => f.size > 10 * 1024 * 1024);
      if (tooLarge.length > 0) {
        setError('Each file must be under 10 MB in size.');
        return;
      }
      setError(null);
      setSelectedFiles((prev) => [...prev, ...files]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const files = Array.from(e.dataTransfer.files);
      const invalid = files.filter(
        (f) => !f.name.toLowerCase().endsWith('.pdf') && !f.name.toLowerCase().endsWith('.txt')
      );
      if (invalid.length > 0) {
        setError('Only PDF (.pdf) and Plain Text (.txt) files are supported.');
        return;
      }
      setSelectedFiles((prev) => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    try {
      setIsUploading(true);
      setError(null);
      const saved = await uploadResumes(selectedFiles);
      onUploadSuccess(saved);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Failed to upload resumes');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Upload Candidate Resumes</h3>
            <p className="text-xs text-slate-500">PDF or TXT documents (Max 10MB each)</p>
          </div>
          <button onClick={onClose} aria-label="Close modal" className="p-1 rounded text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 text-xs">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-md text-rose-700 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Dropzone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl p-8 text-center cursor-pointer bg-slate-50 hover:bg-blue-50/20 transition-colors"
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.txt"
              className="hidden"
              onChange={handleFileChange}
            />
            <UploadCloud className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <p className="font-bold text-slate-800">Click to browse or drag and drop resumes</p>
            <p className="text-slate-500 text-[11px] mt-0.5">Supports single or batch file uploads</p>
          </div>

          {/* Selected File List */}
          {selectedFiles.length > 0 && (
            <div className="space-y-2 max-h-40 overflow-y-auto">
              <span className="font-bold text-slate-700 uppercase tracking-wider text-[11px] block">
                Selected Documents ({selectedFiles.length})
              </span>
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-slate-50 border border-slate-200 rounded">
                  <div className="flex items-center space-x-2 truncate">
                    <FileText className="w-4 h-4 text-slate-500 shrink-0" />
                    <span className="font-medium text-slate-800 truncate">{file.name}</span>
                    <span className="text-slate-400 text-[11px] shrink-0">({(file.size / 1024).toFixed(0)} KB)</span>
                  </div>
                  <button onClick={() => removeFile(idx)} className="text-slate-400 hover:text-rose-600 p-1">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end space-x-2 text-xs">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md bg-white border border-slate-200 text-slate-700 font-semibold"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={isUploading || selectedFiles.length === 0}
            className="px-4 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center space-x-1.5 disabled:opacity-50"
          >
            {isUploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
            <span>{isUploading ? 'Parsing...' : `Upload & Process (${selectedFiles.length})`}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

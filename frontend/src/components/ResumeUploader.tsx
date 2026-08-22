import React, { useState } from 'react';
import { UploadCloud, FileScan, CheckCircle2, AlertCircle, Loader2, X } from 'lucide-react';
import { uploadResumes } from '../services/api';
import { CandidateData } from '../types';

interface ResumeUploaderProps {
  onUploadSuccess: (candidates: CandidateData[]) => void;
}

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB
const ALLOWED_EXTENSIONS = ['.pdf', '.txt'];

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ text: string; isError: boolean } | null>(null);

  const validateAndUploadFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setStatusMsg(null);

    const validFiles: File[] = [];
    const invalidFiles: string[] = [];

    Array.from(files).forEach((file) => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        invalidFiles.push(`'${file.name}' (unsupported extension; only .pdf/.txt allowed)`);
      } else if (file.size > MAX_FILE_SIZE_BYTES) {
        const sizeMb = (file.size / (1024 * 1024)).toFixed(1);
        invalidFiles.push(`'${file.name}' (exceeds 10MB limit: ${sizeMb}MB)`);
      } else {
        validFiles.push(file);
      }
    });

    if (invalidFiles.length > 0) {
      setStatusMsg({
        text: `Upload rejected: ${invalidFiles.join(', ')}`,
        isError: true,
      });
      if (validFiles.length === 0) return;
    }

    try {
      setIsUploading(true);
      setStatusMsg({
        text: `Uploading & parsing ${validFiles.length} file(s) with OCR fallback...`,
        isError: false,
      });

      const newCandidates = await uploadResumes(validFiles);
      onUploadSuccess(newCandidates);
      setStatusMsg({
        text: `Intake complete: Successfully parsed and indexed ${newCandidates.length} candidate file(s).`,
        isError: false,
      });
      setTimeout(() => setStatusMsg(null), 5000);
    } catch (err: any) {
      setStatusMsg({
        text: `Upload failed: ${err.message}`,
        isError: true,
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!isUploading) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (!isUploading) validateAndUploadFiles(e.dataTransfer.files);
      }}
      className={`border border-dashed rounded-lg p-5 transition-all text-center relative ${
        isDragging
          ? 'border-dossier-amber bg-dossier-amberBg/40'
          : 'border-dossier-border bg-dossier-surface/60 hover:border-dossier-borderStrong'
      } ${isUploading ? 'opacity-80 cursor-wait' : ''}`}
    >
      <input
        type="file"
        id="resume-file-input"
        aria-label="Upload PDF or TXT resume files"
        multiple
        accept=".pdf,.txt"
        disabled={isUploading}
        className="hidden"
        onChange={(e) => validateAndUploadFiles(e.target.files)}
      />

      <div className="flex flex-col items-center justify-center space-y-2">
        <div className="w-10 h-10 rounded bg-dossier-subtle border border-dossier-border flex items-center justify-center text-slate-300">
          {isUploading ? (
            <Loader2 className="w-5 h-5 animate-spin text-dossier-amber" />
          ) : (
            <FileScan className="w-5 h-5 text-dossier-amber" />
          )}
        </div>

        <div className="text-xs font-mono text-slate-200">
          {isUploading ? (
            <span className="text-dossier-amber font-bold">Processing upload & OCR extraction in progress...</span>
          ) : (
            <>
              <span>Drop resume documents here, or </span>
              <label
                htmlFor="resume-file-input"
                className="text-dossier-amber hover:underline cursor-pointer font-bold"
              >
                browse file intake
              </label>
            </>
          )}
        </div>

        <p className="text-[11px] font-mono text-slate-500">
          Max 10MB per file • PDF & TXT allowed • Layout parser & OCR fallback • PII redaction
        </p>

        {statusMsg && (
          <div
            className={`mt-2 text-xs font-mono px-3 py-1.5 rounded border inline-flex items-center space-x-2 ${
              statusMsg.isError
                ? 'bg-dossier-unconfirmedBg text-dossier-unconfirmed border-dossier-unconfirmed/50'
                : 'bg-dossier-canvas text-slate-200 border-dossier-border'
            }`}
          >
            {statusMsg.isError ? (
              <AlertCircle className="w-3.5 h-3.5 text-dossier-unconfirmed shrink-0" />
            ) : (
              <CheckCircle2 className="w-3.5 h-3.5 text-dossier-verified shrink-0" />
            )}
            <span>{statusMsg.text}</span>
            <button
              onClick={() => setStatusMsg(null)}
              aria-label="Dismiss upload message"
              className="text-slate-400 hover:text-slate-200 ml-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

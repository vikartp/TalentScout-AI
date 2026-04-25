"use client";

import { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { uploadResumes, listCandidates, clearCandidates } from "@/lib/api";
import { Users, Upload, Loader2, FileUp, Trash2 } from "lucide-react";

export default function CandidatesPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<
    { filename: string; status: string; name?: string; error?: string }[]
  >([]);
  const [candidates, setCandidates] = useState<
    {
      id: number;
      name: string;
      email: string;
      current_role: string;
      current_company: string;
      skills: string[];
      total_experience_years: number;
      filename: string;
    }[]
  >([]);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCandidates();
  }, []);

  async function loadCandidates() {
    try {
      const data = await listCandidates();
      setCandidates(data);
    } catch {
      /* ignore */
    }
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    setUploading(true);
    setError("");
    setUploadResults([]);
    try {
      const result = await uploadResumes(acceptedFiles);
      setUploadResults(result.results);
      await loadCandidates();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    multiple: true,
  });

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Users className="h-6 w-6 text-green-600" />
          Candidates
        </h1>
        {candidates.length > 0 && (
          <button
            onClick={async () => {
              if (!confirm("Delete all candidates?")) return;
              await clearCandidates();
              setCandidates([]);
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors cursor-pointer"
          >
            <Trash2 className="h-3.5 w-3.5" /> Clear All
          </button>
        )}
      </div>

      {/* Upload */}
      <div
        {...getRootProps()}
        className={`bg-white dark:bg-neutral-900 rounded-xl border-2 border-dashed p-10 mb-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950"
            : "border-gray-300 dark:border-neutral-700 hover:border-indigo-400"
        }`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-10 w-10 text-indigo-500 animate-spin" />
            <p className="text-gray-500">Processing resumes...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <FileUp className="h-10 w-10 text-gray-400" />
            <p className="text-gray-600 dark:text-gray-400 font-medium">
              {isDragActive ? "Drop resumes here..." : "Drag & drop resumes (PDF/DOCX) or click to browse"}
            </p>
            <p className="text-sm text-gray-400">Supports multiple files</p>
          </div>
        )}
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="mb-8 bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-4">
          <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Upload Results
          </h3>
          <div className="space-y-1">
            {uploadResults.map((r, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span
                  className={`w-2 h-2 rounded-full ${
                    r.status === "success" ? "bg-green-500" : r.status === "skipped" ? "bg-yellow-500" : "bg-red-500"
                  }`}
                />
                <span className="text-gray-700 dark:text-gray-300">{r.filename}</span>
                {r.name && <span className="text-gray-400">→ {r.name}</span>}
                {r.error && <span className="text-red-400">— {r.error}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Candidate List */}
      <div className="space-y-3">
        {candidates.map((c) => (
          <div
            key={c.id}
            className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">{c.name}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {c.current_role} {c.current_company ? `at ${c.current_company}` : ""} ·{" "}
                  {c.total_experience_years ? `${c.total_experience_years}y exp` : "Exp unknown"}
                </p>
              </div>
              <span className="text-xs text-gray-400 bg-gray-100 dark:bg-neutral-800 px-2 py-1 rounded">
                {c.filename}
              </span>
            </div>
            {c.skills.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {c.skills.slice(0, 8).map((s) => (
                  <span
                    key={s}
                    className="px-2 py-0.5 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 text-xs rounded-full"
                  >
                    {s}
                  </span>
                ))}
                {c.skills.length > 8 && (
                  <span className="px-2 py-0.5 text-xs text-gray-400">+{c.skills.length - 8} more</span>
                )}
              </div>
            )}
          </div>
        ))}
        {candidates.length === 0 && (
          <p className="text-gray-400 text-center py-8">No candidates yet. Upload resumes above.</p>
        )}
      </div>
    </div>
  );
}

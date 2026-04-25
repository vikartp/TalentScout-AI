"use client";

import { useState, useEffect } from "react";
import { parseJD, listJDs, getJD, clearJDs } from "@/lib/api";
import { FileText, Plus, Loader2, ChevronDown, ChevronUp, Trash2, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function JDPage() {
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [jds, setJds] = useState<
    { id: number; title: string; seniority: string; location: string; created_at: string }[]
  >([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [expandedData, setExpandedData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadJDs();
  }, []);

  async function loadJDs() {
    try {
      const data = await listJDs();
      setJds(data);
    } catch {
      /* ignore on initial load */
    }
  }

  async function handleParse() {
    if (!jdText.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await parseJD(jdText);
      setJdText("");
      setExpandedId(result.id);
      setExpandedData(result.parsed);
      await loadJDs();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to parse JD");
    } finally {
      setLoading(false);
    }
  }

  async function toggleExpand(id: number) {
    if (expandedId === id) {
      setExpandedId(null);
      setExpandedData(null);
      return;
    }
    try {
      const data = await getJD(id);
      setExpandedId(id);
      setExpandedData(data.parsed);
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <FileText className="h-6 w-6 text-blue-600" />
          Job Descriptions
        </h1>
        <div className="flex items-center gap-2">
          {jds.length > 0 && (
            <button
              onClick={async () => {
                if (!confirm("Delete all job descriptions?")) return;
                await clearJDs();
                setJds([]);
                setExpandedId(null);
                setExpandedData(null);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors cursor-pointer"
            >
              <Trash2 className="h-3.5 w-3.5" /> Clear All
            </button>
          )}
          {jds.length > 0 && (
            <Link
              href="/candidates"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
            >
              Next: Upload Resumes <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-6 mb-8">
        <h2 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Paste a New Job Description
        </h2>
        <textarea
          className="w-full h-48 p-4 border border-gray-300 dark:border-neutral-700 rounded-lg bg-gray-50 dark:bg-neutral-800 text-sm text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          placeholder="Paste the full job description here..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
        />
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        <button
          onClick={handleParse}
          disabled={loading || !jdText.trim()}
          className="mt-3 px-5 py-2 bg-indigo-600 text-white rounded-lg font-medium text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
          {loading ? "Parsing..." : "Parse JD"}
        </button>
      </div>

      {/* List */}
      <div className="space-y-3">
        {jds.map((jd) => (
          <div
            key={jd.id}
            className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 overflow-hidden"
          >
            <button
              onClick={() => toggleExpand(jd.id)}
              className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors"
            >
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {jd.title || "Untitled JD"}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {jd.seniority} · {jd.location} · JD #{jd.id}
                </p>
              </div>
              {expandedId === jd.id ? (
                <ChevronUp className="h-5 w-5 text-gray-400" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-400" />
              )}
            </button>
            {expandedId === jd.id && expandedData && (
              <div className="border-t border-gray-200 dark:border-neutral-800 p-4">
                <pre className="text-xs text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-neutral-800 p-4 rounded-lg overflow-x-auto">
                  {JSON.stringify(expandedData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        ))}
        {jds.length === 0 && (
          <p className="text-gray-400 text-center py-8">No job descriptions yet. Paste one above to get started.</p>
        )}
      </div>

    </div>
  );
}

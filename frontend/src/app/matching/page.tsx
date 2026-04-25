"use client";

import { useState, useEffect } from "react";
import { listJDs, runMatching, getMatchResults, clearMatches } from "@/lib/api";
import { GitCompareArrows, Loader2, ChevronDown, ChevronUp, Trash2, ArrowRight } from "lucide-react";
import Link from "next/link";

type MatchItem = {
  candidate_id: number;
  candidate_name: string;
  current_role: string;
  match_score: number;
  semantic_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
};

export default function MatchingPage() {
  const [jds, setJds] = useState<{ id: number; title: string }[]>([]);
  const [selectedJd, setSelectedJd] = useState<number | null>(null);
  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [jdTitle, setJdTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    listJDs().then((data) => {
      setJds(data);
      if (data.length > 0) setSelectedJd(data[0].id);
    }).catch(() => {});
  }, []);

  async function handleRunMatching() {
    if (!selectedJd) return;
    setLoading(true);
    setError("");
    try {
      const result = await runMatching(selectedJd);
      setMatches(result.matches);
      setJdTitle(result.jd_title);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Matching failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadExisting() {
    if (!selectedJd) return;
    setLoading(true);
    setError("");
    try {
      const result = await getMatchResults(selectedJd);
      setMatches(result.matches);
    } catch {
      setError("No existing results. Run matching first.");
    } finally {
      setLoading(false);
    }
  }

  function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
    return (
      <div className="flex items-center gap-2 text-xs">
        <span className="w-24 text-gray-500">{label}</span>
        <div className="flex-1 h-2 bg-gray-100 dark:bg-neutral-800 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
        </div>
        <span className="w-10 text-right font-medium text-gray-700 dark:text-gray-300">{value}</span>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <GitCompareArrows className="h-6 w-6 text-purple-600" />
          Candidate Matching
        </h1>
        <div className="flex items-center gap-2">
          {matches.length > 0 && (
            <button
              onClick={async () => {
                if (!confirm("Delete all match results?")) return;
                await clearMatches();
                setMatches([]);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors cursor-pointer"
            >
              <Trash2 className="h-3.5 w-3.5" /> Clear All
            </button>
          )}
          {matches.length > 0 && (
            <Link
              href="/conversations"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors"
            >
              Next: Engage Candidates <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>
      </div>

      {/* JD Selector */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-6 mb-8">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Select Job Description
        </label>
        <div className="flex gap-3">
          <select
            className="flex-1 p-2 border border-gray-300 dark:border-neutral-700 rounded-lg bg-gray-50 dark:bg-neutral-800 text-sm text-gray-900 dark:text-white outline-none"
            value={selectedJd ?? ""}
            onChange={(e) => setSelectedJd(Number(e.target.value) || null)}
          >
            <option value="">Choose a JD...</option>
            {jds.map((jd) => (
              <option key={jd.id} value={jd.id}>
                #{jd.id} — {jd.title || "Untitled"}
              </option>
            ))}
          </select>
          <button
            onClick={handleRunMatching}
            disabled={!selectedJd || loading}
            className="px-5 py-2 bg-purple-600 text-white rounded-lg font-medium text-sm hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <GitCompareArrows className="h-4 w-4" />}
            {loading ? "Matching..." : "Run Matching"}
          </button>
          <button
            onClick={handleLoadExisting}
            disabled={!selectedJd || loading}
            className="px-4 py-2 border border-gray-300 dark:border-neutral-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-neutral-800 disabled:opacity-50"
          >
            Load Existing
          </button>
        </div>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </div>

      {/* Results */}
      {matches.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {jdTitle ? `Results for: ${jdTitle}` : "Match Results"} ({matches.length} candidates)
          </h2>
          {matches.map((m, idx) => (
            <div
              key={m.candidate_id}
              className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 overflow-hidden"
            >
              <button
                onClick={() => setExpandedId(expandedId === m.candidate_id ? null : m.candidate_id)}
                className="w-full p-4 flex items-center gap-4 text-left hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors"
              >
                <span className="text-lg font-bold text-gray-300 w-8">#{idx + 1}</span>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{m.candidate_name}</h3>
                  <p className="text-sm text-gray-500">{m.current_role}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-600">{m.match_score}</div>
                  <div className="text-xs text-gray-400">Match Score</div>
                </div>
                {expandedId === m.candidate_id ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </button>
              {expandedId === m.candidate_id && (
                <div className="border-t border-gray-200 dark:border-neutral-800 p-4 space-y-4">
                  <div className="space-y-2">
                    <ScoreBar label="Semantic" value={m.semantic_score} color="bg-blue-500" />
                    <ScoreBar label="Skills" value={m.skill_score} color="bg-green-500" />
                    <ScoreBar label="Experience" value={m.experience_score} color="bg-amber-500" />
                    <ScoreBar label="Education" value={m.education_score} color="bg-pink-500" />
                  </div>
                  <div className="flex gap-4 text-sm">
                    <div>
                      <span className="font-medium text-green-600">Matched:</span>{" "}
                      {m.matched_skills.length > 0 ? m.matched_skills.join(", ") : "—"}
                    </div>
                    <div>
                      <span className="font-medium text-red-500">Missing:</span>{" "}
                      {m.missing_skills.length > 0 ? m.missing_skills.join(", ") : "—"}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 italic">{m.explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

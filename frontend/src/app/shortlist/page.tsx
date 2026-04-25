"use client";

import { useState, useEffect } from "react";
import { listJDs, getShortlist } from "@/lib/api";
import { ListOrdered, Download, ChevronDown, ChevronUp } from "lucide-react";

type ShortlistItem = {
  candidate_id: number;
  name: string;
  current_role: string;
  current_company: string;
  experience_years: number;
  match_score: number;
  interest_score: number;
  final_score: number;
  matched_skills: string[];
  missing_skills: string[];
  match_explanation: string;
  interest_explanation: string | null;
  conversation_status: string;
  enthusiasm: number | null;
  availability: number | null;
  salary_alignment: number | null;
  cultural_fit: number | null;
};

export default function ShortlistPage() {
  const [jds, setJds] = useState<{ id: number; title: string }[]>([]);
  const [selectedJd, setSelectedJd] = useState<number | null>(null);
  const [jdTitle, setJdTitle] = useState("");
  const [shortlist, setShortlist] = useState<ShortlistItem[]>([]);
  const [matchWeight, setMatchWeight] = useState(0.6);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listJDs().then(setJds).catch(() => {});
  }, []);

  async function handleLoad() {
    if (!selectedJd) return;
    setLoading(true);
    try {
      const data = await getShortlist(selectedJd, matchWeight);
      setShortlist(data.shortlist);
      setJdTitle(data.jd_title);
    } catch {
      setShortlist([]);
    } finally {
      setLoading(false);
    }
  }

  function handleExport() {
    const blob = new Blob([JSON.stringify(shortlist, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `shortlist-jd${selectedJd}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
        <ListOrdered className="h-6 w-6 text-rose-600" />
        Ranked Shortlist
      </h1>

      {/* Controls */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-4 mb-6 flex flex-wrap items-end gap-4">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Job Description</label>
          <select
            className="w-full p-2 border border-gray-300 dark:border-neutral-700 rounded-lg bg-gray-50 dark:bg-neutral-800 text-sm text-gray-900 dark:text-white outline-none"
            value={selectedJd ?? ""}
            onChange={(e) => setSelectedJd(Number(e.target.value) || null)}
          >
            <option value="">Choose...</option>
            {jds.map((jd) => (
              <option key={jd.id} value={jd.id}>
                #{jd.id} — {jd.title || "Untitled"}
              </option>
            ))}
          </select>
        </div>
        <div className="w-48">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Match Weight: {matchWeight} / Interest: {(1 - matchWeight).toFixed(1)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={matchWeight}
            onChange={(e) => setMatchWeight(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
        <button
          onClick={handleLoad}
          disabled={!selectedJd || loading}
          className="px-5 py-2 bg-rose-600 text-white rounded-lg font-medium text-sm hover:bg-rose-700 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Load Shortlist"}
        </button>
        {shortlist.length > 0 && (
          <button
            onClick={handleExport}
            className="px-4 py-2 border border-gray-300 dark:border-neutral-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-neutral-800 flex items-center gap-1"
          >
            <Download className="h-4 w-4" />
            Export JSON
          </button>
        )}
      </div>

      {/* Shortlist Table */}
      {shortlist.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-medium text-gray-500">
            {jdTitle} — {shortlist.length} candidates ranked
          </h2>
          {shortlist.map((c, idx) => (
            <div
              key={c.candidate_id}
              className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 overflow-hidden"
            >
              <button
                onClick={() => setExpandedId(expandedId === c.candidate_id ? null : c.candidate_id)}
                className="w-full p-4 flex items-center gap-4 text-left hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors"
              >
                <span className="text-xl font-bold text-gray-300 w-10 text-center">#{idx + 1}</span>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-white truncate">{c.name}</h3>
                  <p className="text-sm text-gray-500 truncate">
                    {c.current_role} {c.current_company ? `@ ${c.current_company}` : ""} ·{" "}
                    {c.experience_years ? `${c.experience_years}y` : ""}
                  </p>
                </div>
                <div className="flex gap-4 text-center shrink-0">
                  <div>
                    <div className="text-lg font-bold text-purple-600">{c.match_score}</div>
                    <div className="text-[10px] text-gray-400 uppercase">Match</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-orange-600">{c.interest_score || "—"}</div>
                    <div className="text-[10px] text-gray-400 uppercase">Interest</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-rose-600">{c.final_score}</div>
                    <div className="text-[10px] text-gray-400 uppercase">Final</div>
                  </div>
                </div>
                {expandedId === c.candidate_id ? (
                  <ChevronUp className="h-5 w-5 text-gray-400 shrink-0" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400 shrink-0" />
                )}
              </button>
              {expandedId === c.candidate_id && (
                <div className="border-t border-gray-200 dark:border-neutral-800 p-4 space-y-3 text-sm">
                  <div>
                    <span className="font-medium text-green-600">Matched Skills:</span>{" "}
                    {c.matched_skills.join(", ") || "—"}
                  </div>
                  <div>
                    <span className="font-medium text-red-500">Missing Skills:</span>{" "}
                    {c.missing_skills.join(", ") || "—"}
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 italic">{c.match_explanation}</p>
                  {c.interest_explanation && (
                    <div className="p-3 bg-orange-50 dark:bg-orange-950 rounded-lg">
                      <p className="font-medium text-orange-700 dark:text-orange-300 text-xs mb-1">
                        Interest Breakdown — Enthusiasm: {c.enthusiasm}/10, Availability: {c.availability}/10,
                        Salary: {c.salary_alignment}/10, Culture: {c.cultural_fit}/10
                      </p>
                      <p className="text-orange-600 dark:text-orange-400 text-xs">{c.interest_explanation}</p>
                    </div>
                  )}
                  {c.conversation_status === "not_started" && (
                    <p className="text-xs text-gray-400">
                      Outreach not yet conducted. Go to Conversations to engage this candidate.
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

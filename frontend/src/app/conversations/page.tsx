"use client";

import { useState, useEffect } from "react";
import { listJDs, getMatchResults, startConversation, listConversationsByJD, getConversation, clearConversations } from "@/lib/api";
import { MessageSquare, Loader2, User, Bot, Trash2, ArrowRight } from "lucide-react";
import Link from "next/link";

type ConvoResult = {
  id: number;
  candidate_id: number;
  candidate_name: string;
  interest_score: number;
  status: string;
};

type TranscriptMsg = { role: string; content: string };

export default function ConversationsPage() {
  const [jds, setJds] = useState<{ id: number; title: string }[]>([]);
  const [selectedJd, setSelectedJd] = useState<number | null>(null);
  const [matchedCandidates, setMatchedCandidates] = useState<{ candidate_id: number; candidate_name: string; match_score: number }[]>([]);
  const [conversations, setConversations] = useState<ConvoResult[]>([]);
  const [engaging, setEngaging] = useState<number | null>(null);
  const [transcript, setTranscript] = useState<TranscriptMsg[]>([]);
  const [viewingConvo, setViewingConvo] = useState<{
    candidate_name: string;
    scores: Record<string, unknown>;
  } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listJDs().then((data) => {
      setJds(data);
      if (data.length > 0) loadData(data[0].id);
    }).catch(() => {});
  }, []);

  async function loadData(jdId: number) {
    setSelectedJd(jdId);
    try {
      const [matchRes, convoRes] = await Promise.all([
        getMatchResults(jdId).catch(() => ({ matches: [] })),
        listConversationsByJD(jdId).catch(() => []),
      ]);
      setMatchedCandidates(
        matchRes.matches.map((m: { candidate_id: number; candidate_name: string; match_score: number }) => ({
          candidate_id: m.candidate_id,
          candidate_name: m.candidate_name,
          match_score: m.match_score,
        }))
      );
      setConversations(convoRes);
    } catch {
      /* ignore */
    }
  }

  async function handleEngage(candidateId: number) {
    if (!selectedJd) return;
    setEngaging(candidateId);
    setError("");
    try {
      const result = await startConversation(selectedJd, candidateId);
      setTranscript(result.transcript);
      setViewingConvo({
        candidate_name: result.candidate_name,
        scores: result.scores,
      });
      await loadData(selectedJd);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Conversation failed");
    } finally {
      setEngaging(null);
    }
  }

  async function handleViewConvo(convoId: number) {
    try {
      const data = await getConversation(convoId);
      setTranscript(data.transcript);
      setViewingConvo({
        candidate_name: data.candidate_name,
        scores: data.scores,
      });
    } catch {
      /* ignore */
    }
  }

  const convoMap = new Map(conversations.map((c) => [c.candidate_id, c]));

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <MessageSquare className="h-6 w-6 text-orange-600" />
          Conversational Outreach
        </h1>
        <div className="flex items-center gap-2">
          {conversations.length > 0 && (
            <button
              onClick={async () => {
                if (!confirm("Delete all conversations?")) return;
                await clearConversations();
                setConversations([]);
                setTranscript([]);
                setViewingConvo(null);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors cursor-pointer"
            >
              <Trash2 className="h-3.5 w-3.5" /> Clear All
            </button>
          )}
          {conversations.length > 0 && (
            <Link
              href="/shortlist"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg transition-colors"
            >
              Next: View Shortlist <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>
      </div>

      {/* JD Selector */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-4 mb-6">
        <select
          className="w-full p-2 border border-gray-300 dark:border-neutral-700 rounded-lg bg-gray-50 dark:bg-neutral-800 text-sm text-gray-900 dark:text-white outline-none"
          value={selectedJd ?? ""}
          onChange={(e) => {
            const id = Number(e.target.value);
            if (id) loadData(id);
          }}
        >
          <option value="">Select a Job Description...</option>
          {jds.map((jd) => (
            <option key={jd.id} value={jd.id}>
              #{jd.id} — {jd.title || "Untitled"}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: candidates */}
        <div>
          <h2 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Matched Candidates ({matchedCandidates.length})
          </h2>
          <div className="space-y-2">
            {matchedCandidates.map((c) => {
              const convo = convoMap.get(c.candidate_id);
              return (
                <div
                  key={c.candidate_id}
                  className="bg-white dark:bg-neutral-900 rounded-lg border border-gray-200 dark:border-neutral-800 p-3 flex items-center gap-3"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-white text-sm">{c.candidate_name}</p>
                    <p className="text-xs text-gray-400">Match: {c.match_score}</p>
                  </div>
                  {convo?.status === "completed" ? (
                    <button
                      onClick={() => handleViewConvo(convo.id)}
                      className="px-3 py-1 text-xs bg-green-50 text-green-700 rounded-lg hover:bg-green-100 dark:bg-green-950 dark:text-green-300"
                    >
                      View (Interest: {convo.interest_score})
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEngage(c.candidate_id)}
                      disabled={engaging !== null}
                      className="px-3 py-1 text-xs bg-orange-50 text-orange-700 rounded-lg hover:bg-orange-100 dark:bg-orange-950 dark:text-orange-300 disabled:opacity-50 flex items-center gap-1"
                    >
                      {engaging === c.candidate_id ? (
                        <>
                          <Loader2 className="h-3 w-3 animate-spin" /> Engaging...
                        </>
                      ) : (
                        "Engage"
                      )}
                    </button>
                  )}
                </div>
              );
            })}
            {matchedCandidates.length === 0 && selectedJd && (
              <p className="text-gray-400 text-sm text-center py-4">Run matching first from the Matching page.</p>
            )}
          </div>
        </div>

        {/* Right: conversation transcript */}
        <div>
          <h2 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">
            {viewingConvo ? `Conversation: ${viewingConvo.candidate_name}` : "Conversation Transcript"}
          </h2>
          <div className="bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 p-4 min-h-[400px] max-h-[600px] overflow-y-auto">
            {transcript.length > 0 ? (
              <div className="space-y-3">
                {transcript.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex gap-2 ${msg.role === "recruiter" ? "justify-start" : "justify-end"}`}
                  >
                    {msg.role === "recruiter" && <Bot className="h-5 w-5 text-indigo-500 shrink-0 mt-1" />}
                    <div
                      className={`max-w-[80%] p-3 rounded-xl text-sm ${
                        msg.role === "recruiter"
                          ? "bg-indigo-50 dark:bg-indigo-950 text-gray-800 dark:text-gray-200"
                          : "bg-gray-100 dark:bg-neutral-800 text-gray-800 dark:text-gray-200"
                      }`}
                    >
                      {msg.content}
                    </div>
                    {msg.role === "candidate" && <User className="h-5 w-5 text-green-500 shrink-0 mt-1" />}
                  </div>
                ))}
                {viewingConvo?.scores && (
                  <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-950 rounded-lg text-sm">
                    <p className="font-medium text-amber-800 dark:text-amber-300 mb-1">Interest Score Analysis</p>
                    <pre className="text-xs text-amber-700 dark:text-amber-400">
                      {JSON.stringify(viewingConvo.scores, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-400 text-sm text-center py-20">
                Click &quot;Engage&quot; to start a conversation with a candidate.
              </p>
            )}
          </div>
        </div>
      </div>

    </div>
  );
}

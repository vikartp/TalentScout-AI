"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { runAutopilot } from "@/lib/api";
import {
  Zap,
  Upload,
  FileText,
  CheckCircle2,
  XCircle,
  Loader2,
  Rocket,
  ArrowRight,
  Sparkles,
  BrainCircuit,
  Users,
  GitCompareArrows,
  MessageSquare,
  ListOrdered,
  Download,
  RotateCcw,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Agent pipeline steps — shown as a visual progress tracker
const pipelineSteps = [
  { icon: FileText, label: "Parse JD", description: "AI extracts structured requirements" },
  { icon: Users, label: "Process Resumes", description: "Extract profiles & embed" },
  { icon: GitCompareArrows, label: "Match Candidates", description: "4-signal scoring engine" },
  { icon: MessageSquare, label: "Engage Candidates", description: "Simulated conversations" },
  { icon: ListOrdered, label: "Rank & Shortlist", description: "Final ranked output" },
];

export default function AutopilotPage() {
  const router = useRouter();
  const [jdText, setJdText] = useState("");
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [zipFileName, setZipFileName] = useState("");
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState("");
  const [stepsLog, setStepsLog] = useState<string[]>([]);
  const [resultJdId, setResultJdId] = useState<number | null>(null);
  const [activeStep, setActiveStep] = useState(-1);
  const [candidatesProcessed, setCandidatesProcessed] = useState(0);
  const logEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [loadingSample, setLoadingSample] = useState(false);
  const [isRestored, setIsRestored] = useState(false);

  // Clean up WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Restore state from sessionStorage on mount
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("talentScout_autopilotState");
      if (saved) {
        const state = JSON.parse(saved);
        setJdText(state.jdText || "");
        setZipFileName(state.zipFileName || "");
        setCompleted(state.completed || false);
        setError(state.error || "");
        setStepsLog(state.stepsLog || []);
        setResultJdId(state.resultJdId || null);
        setActiveStep(state.activeStep ?? -1);
        setCandidatesProcessed(state.candidatesProcessed || 0);
      }
    } catch (e) {
      console.error("Could not restore Autopilot state", e);
    }
    setIsRestored(true);
  }, []);

  // Save state to sessionStorage on any change
  useEffect(() => {
    if (!isRestored) return; // Don't overwrite with empty initial state
    const state = {
      jdText,
      zipFileName: zipFile?.name || zipFileName,
      completed,
      error,
      stepsLog,
      resultJdId,
      activeStep,
      candidatesProcessed,
    };
    sessionStorage.setItem("talentScout_autopilotState", JSON.stringify(state));
  }, [jdText, zipFile, zipFileName, completed, error, stepsLog, resultJdId, activeStep, candidatesProcessed, isRestored]);

  // Auto-scroll log
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [stepsLog]);

  // Determine active pipeline step from log content
  useEffect(() => {
    if (!running && !completed) {
      setActiveStep(-1);
      return;
    }
    if (completed) {
      setActiveStep(5);
      return;
    }
    const fullLog = stepsLog.join("\n").toLowerCase();

    // LangGraph streams the updated state AFTER a node completes it.
    // Thus, if we see the completion text of Node N, we know the backend is actively working on Node N+1.
    if (fullLog.includes("conversations complete")) setActiveStep(4);
    else if (fullLog.includes("matching complete")) setActiveStep(3);
    else if (fullLog.includes("embedded")) setActiveStep(2);
    else if (fullLog.includes("jd parsed")) setActiveStep(1);
    else setActiveStep(0);
  }, [stepsLog, running, completed]);

  function handleFileDrop(e: React.DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith(".zip")) {
      setZipFile(file);
    }
  }

  async function handleLoadSample() {
    setLoadingSample(true);
    try {
      // Fetch sample ZIP from backend
      const res = await fetch(`${API_URL}/api/autopilot/sample-zip`);
      if (!res.ok) throw new Error("Failed to download sample resumes");
      const blob = await res.blob();
      const file = new File([blob], "sample_resumes.zip", { type: "application/zip" });
      setZipFile(file);

      // Set sample JD
      setJdText(`Senior Full-Stack Developer — TechNova Solutions

Location: Mumbai, India (Hybrid)
Department: Engineering

Role Overview:
We are looking for a Senior Full-Stack Developer to build and scale our core product platform. You will work with modern frontend and backend technologies to deliver high-quality features and mentor junior developers.

Must-Have Skills:
- React.js / Next.js
- Node.js / Express.js
- TypeScript
- PostgreSQL or MongoDB
- REST APIs & GraphQL
- Git & CI/CD pipelines
- Cloud services (AWS or GCP)

Nice-to-Have Skills:
- Docker & Kubernetes
- Redis / message queues
- System design & architecture
- Experience mentoring teams

Experience: 4-7 years of full-stack development experience
Education: Bachelor's degree in Computer Science or related field
Compensation: INR 25-45 LPA`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to load sample data");
    } finally {
      setLoadingSample(false);
    }
  }

  function handleReset() {
    setJdText("");
    setZipFile(null);
    setZipFileName("");
    setStepsLog([]);
    setError("");
    setCompleted(false);
    setResultJdId(null);
    setCandidatesProcessed(0);
    setActiveStep(-1);
    if (fileInputRef.current) fileInputRef.current.value = "";
    sessionStorage.removeItem("talentScout_autopilotState");
  }

  async function handleRun() {
    if (!jdText.trim() || !zipFile) return;
    setRunning(true);
    setCompleted(false);
    setError("");
    setStepsLog(["🚀 Initializing multi-agent pipeline..."]);
    setActiveStep(0);

    const runId = crypto.randomUUID();

    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const wsUrl = `${API_URL.replace(/^http/, "ws")}/api/autopilot/ws/${runId}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "state_update") {
            if (data.steps_log) setStepsLog(data.steps_log);
            if (data.candidates_processed !== undefined) setCandidatesProcessed(data.candidates_processed);
            if (data.error) setError(data.error);
          }
        } catch (e) { }
      };
    } catch (e) {
      console.error("WebSocket connection failed:", e);
    }

    try {
      const result = await runAutopilot(jdText, zipFile, runId);

      if (wsRef.current) {
        wsRef.current.close();
      }

      // Replace with actual logs from the finalized state
      setStepsLog(result.steps_log);
      setResultJdId(result.jd_id);
      setCandidatesProcessed(result.candidates_processed);

      if (result.status === "error") {
        setError(result.error || "Pipeline encountered an error.");
      } else {
        setCompleted(true);
        setActiveStep(5); // all done
      }
    } catch (err: unknown) {
      if (wsRef.current) wsRef.current.close();
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      setRunning(false);
    }
  }

  function handleViewShortlist() {
    if (resultJdId) {
      router.push(`/shortlist`);
    }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white shadow-lg shadow-violet-500/25">
            <Zap className="h-6 w-6" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Autopilot Mode
          </h1>
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white uppercase tracking-wider">
            Multi-Agent
          </span>
        </div>
        <p className="text-gray-500 dark:text-gray-400 ml-14">
          Upload a JD and a ZIP of resumes — our{" "}
          <span className="text-violet-600 dark:text-violet-400 font-medium">5 specialized AI agents</span>{" "}
          will handle everything automatically: parse → match → engage → rank.
        </p>
      </div>

      {/* Pipeline Progress Tracker */}
      <div className="mb-8 bg-white dark:bg-neutral-900 rounded-2xl border border-gray-200 dark:border-neutral-800 p-6 shadow-sm">
        <div className="flex items-center justify-between relative">
          {/* Connecting line */}
          <div className="absolute top-6 left-8 right-8 h-0.5 bg-gray-200 dark:bg-neutral-700" />
          <div
            className="absolute top-6 left-8 h-0.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 transition-all duration-700 ease-out"
            style={{ width: activeStep >= 0 ? `${Math.min((activeStep / 4) * 100, 100)}%` : "0%", maxWidth: "calc(100% - 4rem)" }}
          />

          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            const isActive = idx === activeStep;
            const isDone = idx < activeStep;
            const isPending = idx > activeStep;

            return (
              <div key={idx} className="flex flex-col items-center gap-2 relative z-10">
                <div
                  className={`p-3 rounded-xl border-2 transition-all duration-500 ${isDone
                    ? "bg-green-50 border-green-400 text-green-600 dark:bg-green-950 dark:border-green-600 dark:text-green-400 scale-100"
                    : isActive
                      ? "bg-violet-50 border-violet-400 text-violet-600 dark:bg-violet-950 dark:border-violet-500 dark:text-violet-400 scale-110 shadow-lg shadow-violet-500/20 animate-pulse"
                      : "bg-gray-50 border-gray-200 text-gray-400 dark:bg-neutral-800 dark:border-neutral-700 dark:text-neutral-500"
                    }`}
                >
                  {isDone ? (
                    <CheckCircle2 className="h-5 w-5" />
                  ) : isActive && running ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <span
                  className={`text-xs font-medium text-center transition-colors ${isDone
                    ? "text-green-600 dark:text-green-400"
                    : isActive
                      ? "text-violet-600 dark:text-violet-400"
                      : "text-gray-400 dark:text-neutral-500"
                    }`}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Form */}
        <div className="space-y-5">
          {/* Quick-start helpers */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleLoadSample}
              disabled={running || loadingSample}
              className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-violet-600 bg-violet-50 hover:bg-violet-100 dark:text-violet-400 dark:bg-violet-950/30 dark:hover:bg-violet-950/50 rounded-xl border border-violet-200 dark:border-violet-800 transition-colors disabled:opacity-50 cursor-pointer"
            >
              {loadingSample ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              {loadingSample ? "Loading..." : "Load Sample Data (JD + 12 Resumes)"}
            </button>
            {(jdText || zipFile || zipFileName || stepsLog.length > 0) && (
              <button
                onClick={handleReset}
                disabled={running}
                className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-500 bg-gray-50 hover:bg-gray-100 dark:text-gray-400 dark:bg-neutral-800 dark:hover:bg-neutral-700 rounded-xl border border-gray-200 dark:border-neutral-700 transition-colors disabled:opacity-50 cursor-pointer"
              >
                <RotateCcw className="h-4 w-4" />
                Reset Form
              </button>
            )}
          </div>
          <p className="text-xs text-gray-400 dark:text-neutral-500 -mt-3 ml-1">
            Note: Use 'Load Sample Data' button to test the flow with sample data. It takes around 5-7 minutes to complete the whole process for the sample data. You can ignore it and upload your own JD &amp; resumes below.
          </p>

          {/* JD Input */}
          <div className="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-200 dark:border-neutral-800 p-5 shadow-sm">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              <FileText className="h-4 w-4 text-violet-500" />
              Job Description
            </label>
            <textarea
              id="jd-textarea"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the full job description here..."
              rows={10}
              disabled={running}
              className="w-full p-4 border border-gray-200 dark:border-neutral-700 rounded-xl bg-gray-50 dark:bg-neutral-800 text-sm text-gray-900 dark:text-white resize-none outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 transition-all placeholder:text-gray-400 disabled:opacity-50"
            />
          </div>

          {/* ZIP Upload */}
          <div className="bg-white dark:bg-neutral-900 rounded-2xl border border-gray-200 dark:border-neutral-800 p-5 shadow-sm">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              <Upload className="h-4 w-4 text-violet-500" />
              Resume Pack (.zip)
            </label>
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${(zipFile || zipFileName)
                ? "border-green-400 bg-green-50 dark:bg-green-950/30 dark:border-green-600"
                : "border-gray-300 dark:border-neutral-600 hover:border-violet-400 hover:bg-violet-50/50 dark:hover:bg-violet-950/20"
                } ${running ? "opacity-50 pointer-events-none" : ""}`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".zip"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) setZipFile(file);
                }}
                disabled={running}
              />
              {zipFile || zipFileName ? (
                <div className="flex flex-col items-center gap-2">
                  <CheckCircle2 className="h-8 w-8 text-green-500" />
                  <span className="text-sm font-medium text-green-700 dark:text-green-400">
                    {zipFile ? zipFile.name : zipFileName}
                  </span>
                  <span className="text-xs text-gray-500">
                    {zipFile ? `${(zipFile.size / 1024).toFixed(1)} KB` : "Session Restored File"} — Click to change
                  </span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload className="h-8 w-8 text-gray-400" />
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    Drop a <span className="font-semibold">.zip</span> file with resumes (PDF/DOCX)
                  </span>
                  <span className="text-xs text-gray-400">or click to browse</span>
                </div>
              )}
            </div>
          </div>

          {/* Run Button */}
          <button
            id="autopilot-run-btn"
            onClick={handleRun}
            disabled={running || !jdText.trim() || !zipFile}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl font-semibold text-white text-base transition-all disabled:opacity-40 disabled:cursor-not-allowed bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 shadow-lg hover:shadow-xl shadow-violet-500/25 hover:shadow-violet-500/40 cursor-pointer active:scale-[0.98]"
          >
            {running ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Agents are working...
              </>
            ) : (
              <>
                <Rocket className="h-5 w-5" />
                Launch Autopilot Pipeline
              </>
            )}
          </button>
        </div>

        {/* Right Column: Live Log & Results */}
        <div className="space-y-5">
          {/* Live Agent Log */}
          <div className="bg-neutral-900 dark:bg-neutral-950 rounded-2xl border border-neutral-700 shadow-sm overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-neutral-700 bg-neutral-800">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <span className="text-xs font-mono text-neutral-400 ml-2">
                agent-pipeline.log
              </span>
              {running && (
                <span className="ml-auto flex items-center gap-1.5 text-xs text-green-400">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                  LIVE
                </span>
              )}
            </div>
            <div className="p-4 max-h-[400px] overflow-y-auto font-mono text-xs space-y-1">
              {stepsLog.length === 0 ? (
                <div className="text-neutral-500 flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Awaiting launch...
                </div>
              ) : (
                stepsLog.map((line, i) => (
                  <div
                    key={i}
                    className={`py-0.5 ${line.startsWith("❌")
                      ? "text-red-400"
                      : line.startsWith("⚠️")
                        ? "text-yellow-400"
                        : line.startsWith("✅")
                          ? "text-green-400"
                          : line.includes("🚀")
                            ? "text-violet-400"
                            : "text-neutral-300"
                      }`}
                  >
                    {line}
                  </div>
                ))
              )}
              <div ref={logEndRef} />
            </div>
          </div>

          {/* Error state */}
          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl flex items-start gap-3">
              <XCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-700 dark:text-red-300">Pipeline Error</p>
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Success state */}
          {completed && resultJdId && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border border-green-200 dark:border-green-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-green-100 dark:bg-green-900">
                  <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h3 className="font-bold text-green-800 dark:text-green-300 text-lg">
                    Pipeline Complete!
                  </h3>
                  <p className="text-sm text-green-600 dark:text-green-400">
                    {candidatesProcessed} candidate(s) processed end-to-end
                  </p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-white/70 dark:bg-neutral-900/50 rounded-xl p-3 text-center">
                  <BrainCircuit className="h-5 w-5 text-violet-500 mx-auto mb-1" />
                  <div className="text-lg font-bold text-gray-900 dark:text-white">5</div>
                  <div className="text-[10px] text-gray-500 uppercase">Agents Used</div>
                </div>
                <div className="bg-white/70 dark:bg-neutral-900/50 rounded-xl p-3 text-center">
                  <Users className="h-5 w-5 text-blue-500 mx-auto mb-1" />
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {candidatesProcessed}
                  </div>
                  <div className="text-[10px] text-gray-500 uppercase">Candidates</div>
                </div>
                <div className="bg-white/70 dark:bg-neutral-900/50 rounded-xl p-3 text-center">
                  <Sparkles className="h-5 w-5 text-amber-500 mx-auto mb-1" />
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {stepsLog.filter((l) => l.startsWith("✅")).length}
                  </div>
                  <div className="text-[10px] text-gray-500 uppercase">Steps Done</div>
                </div>
              </div>

              <button
                id="view-shortlist-btn"
                onClick={handleViewShortlist}
                className="w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 shadow-lg shadow-green-500/25 transition-all cursor-pointer active:scale-[0.98]"
              >
                View Ranked Shortlist
                <ArrowRight className="h-5 w-5" />
              </button>

              <p className="text-xs text-green-600/70 dark:text-green-400/50 text-center">
                All data is available in the manual workflow pages too — you can refine from any step.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

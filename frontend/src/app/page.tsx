"use client";

import { useState } from "react";
import Link from "next/link";
import {
  FileText,
  Users,
  GitCompareArrows,
  MessageSquare,
  ListOrdered,
  ArrowRight,
  Trash2,
} from "lucide-react";
import { resetDatabase } from "@/lib/api";

const steps = [
  {
    icon: FileText,
    title: "1. Paste a Job Description",
    description: "AI parses it into structured requirements",
    href: "/jd",
    color: "bg-blue-50 text-blue-600",
  },
  {
    icon: Users,
    title: "2. Upload Resumes",
    description: "PDF/DOCX — AI extracts candidate profiles",
    href: "/candidates",
    color: "bg-green-50 text-green-600",
  },
  {
    icon: GitCompareArrows,
    title: "3. Match Candidates",
    description: "Semantic + structured scoring against the JD",
    href: "/matching",
    color: "bg-purple-50 text-purple-600",
  },
  {
    icon: MessageSquare,
    title: "4. Engage Candidates",
    description: "Simulated outreach to gauge interest",
    href: "/conversations",
    color: "bg-orange-50 text-orange-600",
  },
  {
    icon: ListOrdered,
    title: "5. View Shortlist",
    description: "Ranked by Match Score + Interest Score",
    href: "/shortlist",
    color: "bg-rose-50 text-rose-600",
  },
];

export default function Home() {
  const [clearing, setClearing] = useState(false);

  async function handleClearDB() {
    if (!confirm("This will delete ALL data (JDs, candidates, matches, conversations). Continue?")) return;
    setClearing(true);
    try {
      await resetDatabase();
      alert("Database cleared successfully.");
    } catch (err: unknown) {
      alert("Failed to clear database: " + (err instanceof Error ? err.message : err));
    } finally {
      setClearing(false);
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-10 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            TalentScout AI
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            AI-Powered Talent Scouting & Engagement Agent — from JD to ranked
            shortlist in minutes.
          </p>
        </div>
        <button
          onClick={handleClearDB}
          disabled={clearing}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors disabled:opacity-50 cursor-pointer"
        >
          <Trash2 className="h-4 w-4" />
          {clearing ? "Clearing..." : "Clear Database"}
        </button>
      </div>

      <div className="space-y-4">
        {steps.map(({ icon: Icon, title, description, href, color }) => (
          <Link
            key={href}
            href={href}
            className="flex items-center gap-4 p-5 bg-white dark:bg-neutral-900 rounded-xl border border-gray-200 dark:border-neutral-800 hover:shadow-md transition-shadow group"
          >
            <div className={`p-3 rounded-lg ${color}`}>
              <Icon className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {description}
              </p>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-300 group-hover:text-indigo-500 transition-colors" />
          </Link>
        ))}
      </div>
    </div>
  );
}

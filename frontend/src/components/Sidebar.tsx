"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import {
  FileText,
  Users,
  GitCompareArrows,
  MessageSquare,
  ListOrdered,
  BrainCircuit,
  Zap,
  Sun,
  Moon,
  Heart,
} from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: BrainCircuit },
  { href: "/autopilot", label: "Autopilot", icon: Zap, highlight: true },
  { href: "/jd", label: "Job Descriptions", icon: FileText },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/matching", label: "Matching", icon: GitCompareArrows },
  { href: "/conversations", label: "Conversations", icon: MessageSquare },
  { href: "/shortlist", label: "Shortlist", icon: ListOrdered },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <aside className="w-64 shrink-0 bg-white dark:bg-neutral-900 border-r border-gray-200 dark:border-neutral-800 flex flex-col h-full">
      <div className="p-5 border-b border-gray-200 dark:border-neutral-800">
        <Link href="/" className="flex items-center gap-2">
          <BrainCircuit className="h-7 w-7 text-indigo-600" />
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            TalentScout AI
          </span>
        </Link>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {nav.map(({ href, label, icon: Icon, highlight }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          const isHighlight = highlight && !active;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${active
                ? highlight
                  ? "bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/20"
                  : "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                : isHighlight
                  ? "text-violet-600 dark:text-violet-400 hover:bg-violet-50 dark:hover:bg-violet-950/50 bg-violet-50/50 dark:bg-violet-950/20 border border-violet-200 dark:border-violet-800"
                  : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-neutral-800"
                }`}
            >
              <Icon className="h-4 w-4" />
              {label}
              {highlight && !active && (
                <span className="ml-auto px-2 py-0.5 text-[9px] font-bold rounded-md bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white uppercase flex items-center gap-1 shadow-sm shadow-fuchsia-500/20">
                  Preferred <Heart className="h-2.5 w-2.5 fill-white text-white drop-shadow-sm" />
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 mt-auto">
        <div className="relative overflow-hidden bg-gradient-to-br from-indigo-50/80 via-white to-violet-50/80 dark:from-indigo-950/30 dark:via-neutral-900 dark:to-violet-950/30 border border-indigo-100/50 dark:border-indigo-500/10 rounded-2xl p-4 flex flex-col gap-4 shadow-sm">
          {/* Subtle background glow */}
          <div className="absolute -top-4 -right-4 w-24 h-24 bg-violet-400/20 dark:bg-violet-600/10 rounded-full blur-xl pointer-events-none" />
          <div className="absolute -bottom-4 -left-4 w-24 h-24 bg-indigo-400/20 dark:bg-indigo-600/10 rounded-full blur-xl pointer-events-none" />

          {mounted && (
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="group relative z-10 flex items-center justify-center w-fit mx-auto px-4 py-2.5 rounded-xl bg-white/60 dark:bg-neutral-800/60 border border-white/60 dark:border-neutral-700/50 hover:bg-white dark:hover:bg-neutral-800 text-sm font-semibold text-gray-700 dark:text-gray-300 transition-all duration-300 shadow-[0_2px_10px_rgb(0,0,0,0.02)] hover:shadow-[0_4px_15px_rgb(0,0,0,0.05)] dark:shadow-none cursor-pointer backdrop-blur-md"
            >
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-500/20 transition-all duration-300">
                  {theme === "dark" ? <Moon className="h-3.5 w-3.5" /> : <Sun className="h-3.5 w-3.5" />}
                </div>
                <span>{theme === "dark" ? "Dark Theme" : "Light Theme"}</span>
              </div>
            </button>
          )}

          <div className="z-10 flex flex-col items-center justify-center pt-1 pb-0.5">
            <span className="text-[11px] font-bold text-gray-600 dark:text-neutral-400 flex items-center gap-1 cursor-default">
              Built By
              <a
                href="https://www.linkedin.com/in/vikash-kumar-835b31ba"
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:underline transition-colors cursor-pointer mx-0.5"
              >
                Vikash Kumar
              </a>
              With
              <span className="animate-pulse inline-block text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.6)] scale-110 ml-0.5">❤️</span>
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

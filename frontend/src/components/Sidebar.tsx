"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FileText,
  Users,
  GitCompareArrows,
  MessageSquare,
  ListOrdered,
  BrainCircuit,
} from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: BrainCircuit },
  { href: "/jd", label: "Job Descriptions", icon: FileText },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/matching", label: "Matching", icon: GitCompareArrows },
  { href: "/conversations", label: "Conversations", icon: MessageSquare },
  { href: "/shortlist", label: "Shortlist", icon: ListOrdered },
];

export default function Sidebar() {
  const pathname = usePathname();

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
        {nav.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                  : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-neutral-800"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-200 dark:border-neutral-800 text-xs text-gray-400">
        Catalyst Hackathon 2026
      </div>
    </aside>
  );
}

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { ThemeProvider } from "@/components/ThemeProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TalentScout AI",
  description: "AI-Powered Talent Scouting & Engagement Agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="h-full flex">
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <div className="w-64 h-full sticky top-0 z-30">
            <Sidebar />
          </div>
          <main className="flex-1 h-full overflow-y-auto bg-gray-50 dark:bg-neutral-950">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}

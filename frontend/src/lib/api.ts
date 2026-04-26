const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// --- Reset ---

export async function resetDatabase() {
  return request<{ message: string }>("/api/reset", { method: "DELETE" });
}

export async function clearJDs() {
  return request<{ message: string }>("/api/jd/clear", { method: "DELETE" });
}

export async function clearCandidates() {
  return request<{ message: string }>("/api/candidates/clear", { method: "DELETE" });
}

export async function clearMatches() {
  return request<{ message: string }>("/api/matching/clear", { method: "DELETE" });
}

export async function clearConversations() {
  return request<{ message: string }>("/api/conversations/clear", { method: "DELETE" });
}

// --- Job Descriptions ---

export async function parseJD(text: string) {
  return request<{ id: number; parsed: Record<string, unknown> }>("/api/jd/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export async function getJD(id: number) {
  return request<{
    id: number;
    raw_text: string;
    parsed: Record<string, unknown>;
    created_at: string;
  }>(`/api/jd/${id}`);
}

export async function listJDs() {
  return request<
    { id: number; title: string; seniority: string; location: string; created_at: string }[]
  >("/api/jd");
}

// --- Candidates ---

export async function uploadResumes(files: File[]) {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  return request<{
    results: { filename: string; status: string; candidate_id?: number; name?: string; error?: string }[];
  }>("/api/candidates/upload", {
    method: "POST",
    body: formData,
  });
}

export async function listCandidates() {
  return request<
    {
      id: number;
      name: string;
      email: string;
      current_role: string;
      current_company: string;
      skills: string[];
      total_experience_years: number;
      filename: string;
      created_at: string;
    }[]
  >("/api/candidates");
}

export async function deleteCandidate(id: number) {
  return request<{ message: string }>(`/api/candidates/${id}`, { method: "DELETE" });
}

export async function getCandidate(id: number) {
  return request<Record<string, unknown>>(`/api/candidates/${id}`);
}

// --- Matching ---

export async function runMatching(jdId: number) {
  return request<{
    jd_id: number;
    jd_title: string;
    matches: {
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
    }[];
  }>("/api/matching/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jd_id: jdId }),
  });
}

export async function getMatchResults(jdId: number) {
  return request<{
    jd_id: number;
    matches: {
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
    }[];
  }>(`/api/matching/results/${jdId}`);
}

// --- Conversations ---

export async function startConversation(jdId: number, candidateId: number) {
  return request<{
    id: number;
    jd_id: number;
    candidate_id: number;
    candidate_name: string;
    transcript: { role: string; content: string }[];
    scores: {
      interest_score: number;
      enthusiasm: number;
      availability: number;
      salary_alignment: number;
      cultural_fit: number;
      explanation: string;
    };
    status: string;
  }>("/api/conversations/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jd_id: jdId, candidate_id: candidateId }),
  });
}

export async function getConversation(id: number) {
  return request<{
    id: number;
    jd_id: number;
    candidate_id: number;
    candidate_name: string;
    transcript: { role: string; content: string }[];
    scores: {
      interest_score: number;
      enthusiasm: number;
      availability: number;
      salary_alignment: number;
      cultural_fit: number;
      explanation: string;
    };
    status: string;
  }>(`/api/conversations/${id}`);
}

export async function listConversationsByJD(jdId: number) {
  return request<
    { id: number; candidate_id: number; candidate_name: string; interest_score: number; status: string }[]
  >(`/api/conversations/by-jd/${jdId}`);
}

// --- Shortlist ---

export async function getShortlist(jdId: number, matchWeight: number = 0.6) {
  return request<{
    jd_id: number;
    jd_title: string;
    match_weight: number;
    interest_weight: number;
    shortlist: {
      candidate_id: number;
      name: string;
      current_role: string;
      current_company: string;
      experience_years: number;
      match_score: number;
      semantic_score: number;
      skill_score: number;
      experience_score: number;
      education_score: number;
      matched_skills: string[];
      missing_skills: string[];
      match_explanation: string;
      interest_score: number;
      enthusiasm: number | null;
      availability: number | null;
      salary_alignment: number | null;
      cultural_fit: number | null;
      interest_explanation: string | null;
      conversation_id: number | null;
      conversation_status: string;
      final_score: number;
    }[];
  }>(`/api/shortlist/${jdId}?match_weight=${matchWeight}`);
}

// --- Autopilot (Multi-Agent Pipeline) ---

export async function runAutopilot(jdText: string, resumesZip: File) {
  const formData = new FormData();
  formData.append("jd_text", jdText);
  formData.append("resumes_zip", resumesZip);

  const res = await fetch(`${API_URL}/api/autopilot/run`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }

  return res.json() as Promise<{
    status: string;
    jd_id: number;
    jd_parsed: Record<string, unknown>;
    candidates_processed: number;
    shortlist: {
      candidate_id: number;
      name: string;
      current_role: string;
      current_company: string;
      experience_years: number;
      match_score: number;
      interest_score: number;
      final_score: number;
    }[];
    steps_log: string[];
    error: string;
  }>;
}

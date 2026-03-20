const BASE = "";

async function authHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  try {
    const { getAccessToken } = await import("./supabase");
    const token = await getAccessToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  } catch {
    // No auth — demo mode
  }
  return headers;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = await authHeaders();
  const res = await fetch(`${BASE}${path}`, { ...options, headers: { ...headers, ...options.headers } });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// Papers
export const papers = {
  list: (params?: Record<string, string>) =>
    request<{ papers: any[] }>(`/api/papers/?${new URLSearchParams(params)}`),
  get: (id: string) => request<any>(`/api/papers/${id}`),
  submitUrl: (url: string) =>
    request<any>("/api/papers/url", { method: "POST", body: JSON.stringify({ url }) }),
  delete: (id: string) =>
    request<any>(`/api/papers/${id}`, { method: "DELETE" }),
};

// Gaps
export const gaps = {
  analyze: (source_ids: string[]) =>
    request<any>("/api/gaps/analyze", { method: "POST", body: JSON.stringify({ source_ids }) }),
  list: () => request<{ reports: any[] }>("/api/gaps/reports"),
  get: (id: string) => request<any>(`/api/gaps/reports/${id}`),
  feedback: (reportId: string, gapIndex: number, outcome: string, modification?: string) =>
    request<any>(`/api/gaps/reports/${reportId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ gap_index: gapIndex, outcome, modification }),
    }),
};

// Q&A
export const qa = {
  ask: (query: string, source_ids?: string[]) =>
    request<any>("/api/qa/ask", { method: "POST", body: JSON.stringify({ query, source_ids }) }),
  history: () => request<{ queries: any[] }>("/api/qa/history"),
};

// Compare
export const compare = {
  generate: (source_ids: string[]) =>
    request<any>("/api/compare/generate", { method: "POST", body: JSON.stringify({ source_ids }) }),
  get: (id: string) => request<any>(`/api/compare/${id}`),
};

// Experiment
export const experiment = {
  design: (gap_description: string, context?: string) =>
    request<any>("/api/experiment/design", {
      method: "POST",
      body: JSON.stringify({ gap_description, context }),
    }),
  history: () => request<{ experiments: any[] }>("/api/experiment/history"),
};

// Memory
export const memory = {
  welcome: () => request<{ message: string }>("/api/memory/welcome"),
  sessions: () => request<{ sessions: any[] }>("/api/memory/sessions"),
  startSession: (name: string, focus: string) =>
    request<any>("/api/memory/sessions/start", {
      method: "POST",
      body: JSON.stringify({ session_name: name, clinical_focus: focus }),
    }),
  knowledgeGraph: () => request<any>("/api/memory/knowledge-graph"),
  patterns: () => request<any>("/api/memory/patterns"),
};

// Benchmark
export const benchmark = {
  leaderboard: () => request<any>("/api/benchmark/leaderboard"),
  tasks: () => request<any>("/api/benchmark/tasks"),
};

// Auth
export const auth = {
  me: () => request<any>("/api/auth/me"),
};

"use client";

import { useEffect, useState } from "react";
import { FileText, Search, MessageSquare, FlaskConical } from "lucide-react";
import * as api from "@/lib/api";

export default function DashboardPage() {
  const [welcome, setWelcome] = useState("");
  const [papers, setPapers] = useState<any[]>([]);
  const [urlInput, setUrlInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.memory.welcome().then((d) => setWelcome(d.message)).catch(() => {});
    api.papers.list().then((d) => setPapers(d.papers)).catch(() => {});
  }, []);

  const submitUrl = async () => {
    if (!urlInput.trim()) return;
    setLoading(true);
    try {
      await api.papers.submitUrl(urlInput);
      setUrlInput("");
      const d = await api.papers.list();
      setPapers(d.papers);
    } catch (err: any) {
      alert(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <nav className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold gradient-text">MedResearch Mind</h1>
        <div className="flex gap-4 text-sm">
          <a href="/dashboard" className="text-accent">Dashboard</a>
          <a href="/library" className="text-muted hover:text-foreground">Library</a>
          <a href="/gaps" className="text-muted hover:text-foreground">Gaps</a>
          <a href="/chat" className="text-muted hover:text-foreground">Q&A</a>
          <a href="/compare" className="text-muted hover:text-foreground">Compare</a>
          <a href="/experiment" className="text-muted hover:text-foreground">PICO</a>
          <a href="/benchmark" className="text-muted hover:text-foreground">Bench</a>
        </div>
      </nav>

      {welcome && (
        <div className="bg-card-bg border border-card-border rounded-xl p-4 mb-6">
          <p className="text-sm text-muted">{welcome}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-card-bg border border-card-border rounded-xl p-4">
          <FileText className="w-5 h-5 text-accent mb-2" />
          <p className="text-2xl font-bold">{papers.length}</p>
          <p className="text-xs text-muted">Papers</p>
        </div>
        <a href="/gaps" className="bg-card-bg border border-card-border rounded-xl p-4 hover:border-accent transition-colors">
          <Search className="w-5 h-5 text-accent mb-2" />
          <p className="text-sm font-semibold">Find Gaps</p>
          <p className="text-xs text-muted">Analyze your papers</p>
        </a>
        <a href="/chat" className="bg-card-bg border border-card-border rounded-xl p-4 hover:border-accent transition-colors">
          <MessageSquare className="w-5 h-5 text-accent mb-2" />
          <p className="text-sm font-semibold">Ask Questions</p>
          <p className="text-xs text-muted">Grounded Q&A</p>
        </a>
        <a href="/experiment" className="bg-card-bg border border-card-border rounded-xl p-4 hover:border-accent transition-colors">
          <FlaskConical className="w-5 h-5 text-accent mb-2" />
          <p className="text-sm font-semibold">Design Experiment</p>
          <p className="text-xs text-muted">PICO format</p>
        </a>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Add a source</h2>
        <div className="flex gap-3">
          <input
            type="text" value={urlInput} onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Paste ArXiv, PubMed, YouTube, GitHub, or any URL..."
            className="flex-1 px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent"
            onKeyDown={(e) => e.key === "Enter" && submitUrl()}
          />
          <button onClick={submitUrl} disabled={loading}
            className="px-6 py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-lg transition-colors disabled:opacity-50">
            {loading ? "Processing..." : "Add"}
          </button>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Recent Papers</h2>
        <div className="space-y-2">
          {papers.slice(0, 10).map((p) => (
            <div key={p.id} className="bg-card-bg border border-card-border rounded-lg p-3 flex items-start justify-between">
              <div>
                <p className="font-medium text-sm">{p.title || "Untitled"}</p>
                <div className="flex gap-2 mt-1 flex-wrap">
                  <span className="text-xs px-2 py-0.5 bg-zinc-800 rounded">{p.source_type}</span>
                  {(p.imaging_modalities || []).map((m: string) => (
                    <span key={m} className="text-xs px-2 py-0.5 bg-accent/10 text-accent rounded">{m}</span>
                  ))}
                  {(p.conditions || []).map((c: string) => (
                    <span key={c} className="text-xs px-2 py-0.5 bg-emerald-900/30 text-emerald-400 rounded">{c}</span>
                  ))}
                </div>
              </div>
              <span className="text-xs text-muted">{p.published_date || ""}</span>
            </div>
          ))}
          {papers.length === 0 && (
            <p className="text-sm text-muted py-8 text-center">No papers yet. Add your first source above.</p>
          )}
        </div>
      </div>
    </div>
  );
}

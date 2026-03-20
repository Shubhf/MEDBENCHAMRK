"use client";

import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import * as api from "@/lib/api";

export default function LibraryPage() {
  const [papers, setPapers] = useState<any[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => { api.papers.list().then((d) => setPapers(d.papers)).catch(() => {}); }, []);

  const filtered = papers.filter((p) => {
    if (!filter) return true;
    const f = filter.toLowerCase();
    return (p.title || "").toLowerCase().includes(f) ||
      (p.imaging_modalities || []).some((m: string) => m.toLowerCase().includes(f)) ||
      (p.conditions || []).some((c: string) => c.toLowerCase().includes(f));
  });

  const remove = async (id: string) => {
    await api.papers.delete(id);
    setPapers((prev) => prev.filter((p) => p.id !== id));
  };

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <a href="/dashboard" className="text-accent text-sm mb-4 inline-block">&larr; Dashboard</a>
      <h1 className="text-2xl font-bold mb-6">Paper Library</h1>
      <input type="text" value={filter} onChange={(e) => setFilter(e.target.value)}
        placeholder="Search by title, modality, or condition..."
        className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent mb-6" />
      <div className="space-y-2">
        {filtered.map((p) => (
          <div key={p.id} className="bg-card-bg border border-card-border rounded-lg p-4 flex items-start justify-between">
            <div className="flex-1">
              <p className="font-medium">{p.title || "Untitled"}</p>
              <p className="text-xs text-muted mt-1">{(p.authors || []).slice(0, 3).join(", ")} | {p.journal_or_venue || p.source_type}</p>
              <div className="flex gap-2 mt-2 flex-wrap">
                {(p.imaging_modalities || []).map((m: string) => <span key={m} className="text-xs px-2 py-0.5 bg-accent/10 text-accent rounded">{m}</span>)}
                {(p.conditions || []).map((c: string) => <span key={c} className="text-xs px-2 py-0.5 bg-emerald-900/30 text-emerald-400 rounded">{c}</span>)}
                {(p.architectures || []).map((a: string) => <span key={a} className="text-xs px-2 py-0.5 bg-purple-900/30 text-purple-400 rounded">{a}</span>)}
              </div>
            </div>
            <button onClick={() => remove(p.id)} className="p-2 text-muted hover:text-red-400"><Trash2 className="w-4 h-4" /></button>
          </div>
        ))}
        {filtered.length === 0 && <p className="text-center text-muted py-8">No papers found.</p>}
      </div>
    </div>
  );
}

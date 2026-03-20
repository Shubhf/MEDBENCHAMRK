"use client";

import { useEffect, useState } from "react";
import { Check, X, Edit2, Download } from "lucide-react";
import * as api from "@/lib/api";

export default function GapsPage() {
  const [papers, setPapers] = useState<any[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.papers.list().then((d) => setPapers(d.papers)).catch(() => {});
  }, []);

  const toggleSelect = (id: string) => {
    setSelected((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  };

  const analyze = async () => {
    if (selected.length < 2) { alert("Select at least 2 papers"); return; }
    setLoading(true);
    try {
      const result = await api.gaps.analyze(selected);
      setReport(result);
    } catch (err: any) { alert(err.message); }
    setLoading(false);
  };

  const sendFeedback = async (idx: number, outcome: string) => {
    if (!report?.id) return;
    await api.gaps.feedback(report.id, idx, outcome);
    const updatedGaps = [...report.gaps];
    updatedGaps[idx] = { ...updatedGaps[idx], _feedback: outcome };
    setReport({ ...report, gaps: updatedGaps });
  };

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <a href="/dashboard" className="text-accent text-sm mb-4 inline-block">&larr; Dashboard</a>
      <h1 className="text-2xl font-bold mb-6">Medical AI Gap Finder</h1>

      {!report && (
        <>
          <p className="text-muted text-sm mb-4">Select papers to analyze for research gaps:</p>
          <div className="space-y-2 mb-6 max-h-80 overflow-y-auto">
            {papers.map((p) => (
              <label key={p.id} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                selected.includes(p.id) ? "bg-accent/10 border-accent" : "bg-card-bg border-card-border hover:border-zinc-600"
              }`}>
                <input type="checkbox" checked={selected.includes(p.id)} onChange={() => toggleSelect(p.id)} className="rounded" />
                <div>
                  <p className="text-sm font-medium">{p.title || "Untitled"}</p>
                  <p className="text-xs text-muted">{p.source_type} | {(p.conditions || []).join(", ")}</p>
                </div>
              </label>
            ))}
          </div>
          <button onClick={analyze} disabled={loading || selected.length < 2}
            className="px-8 py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-lg disabled:opacity-50">
            {loading ? "Analyzing..." : `Find Gaps (${selected.length} papers)`}
          </button>
        </>
      )}

      {report && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold">{report.clinical_topic}</h2>
              <p className="text-sm text-muted">{report.summary}</p>
            </div>
            <button onClick={() => setReport(null)} className="text-sm text-muted hover:text-foreground">New Analysis</button>
          </div>

          <div className="space-y-4">
            {(report.gaps || []).map((gap: any, i: number) => (
              <div key={i} className="bg-card-bg border border-card-border rounded-xl p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="text-xs px-2 py-1 bg-accent/10 text-accent rounded-full">{gap.gap_type}</span>
                    <h3 className="text-base font-semibold mt-2">{gap.description}</h3>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => sendFeedback(i, "accepted")}
                      className={`p-2 rounded-lg transition-colors ${gap._feedback === "accepted" ? "bg-green-900/30 text-green-400" : "hover:bg-zinc-800 text-muted"}`}>
                      <Check className="w-4 h-4" />
                    </button>
                    <button onClick={() => sendFeedback(i, "rejected")}
                      className={`p-2 rounded-lg transition-colors ${gap._feedback === "rejected" ? "bg-red-900/30 text-red-400" : "hover:bg-zinc-800 text-muted"}`}>
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="flex gap-4 text-xs text-muted mb-3">
                  <span>Clinical Relevance: <span className="text-foreground">{(gap.clinical_relevance_score * 100).toFixed(0)}%</span></span>
                  <span>Feasibility: <span className="text-foreground">{(gap.feasibility_score * 100).toFixed(0)}%</span></span>
                </div>
                {gap.evidence?.length > 0 && (
                  <div className="bg-zinc-900/50 rounded-lg p-3 mb-3">
                    <p className="text-xs text-muted mb-1">Evidence:</p>
                    {gap.evidence.map((e: any, j: number) => (
                      <p key={j} className="text-xs text-zinc-400">&bull; <span className="text-foreground">{e.paper_title}:</span> {e.observation}</p>
                    ))}
                  </div>
                )}
                {gap.suggested_experiment && (
                  <p className="text-xs text-muted"><span className="text-accent">Suggested experiment:</span> {gap.suggested_experiment}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

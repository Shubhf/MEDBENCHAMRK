"use client";

import { useState } from "react";
import * as api from "@/lib/api";

export default function ExperimentPage() {
  const [gap, setGap] = useState("");
  const [context, setContext] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const design = async () => {
    if (!gap.trim()) return;
    setLoading(true);
    try {
      const r = await api.experiment.design(gap, context);
      setResult(r);
    } catch (err: any) { alert(err.message); }
    setLoading(false);
  };

  return (
    <div className="min-h-screen p-6 max-w-4xl mx-auto">
      <a href="/dashboard" className="text-accent text-sm mb-4 inline-block">&larr; Dashboard</a>
      <h1 className="text-2xl font-bold mb-6">PICO Experiment Designer</h1>

      {!result && (
        <div className="space-y-4">
          <textarea value={gap} onChange={(e) => setGap(e.target.value)} rows={3}
            placeholder="Describe the research gap... e.g., 'No transformer-based approaches for retinal vessel segmentation on the DRIVE dataset'"
            className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent" />
          <textarea value={context} onChange={(e) => setContext(e.target.value)} rows={2}
            placeholder="Additional context (optional)..."
            className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent" />
          <button onClick={design} disabled={loading || !gap.trim()}
            className="px-8 py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-lg disabled:opacity-50">
            {loading ? "Designing..." : "Design Experiment"}
          </button>
        </div>
      )}

      {result && !result.error && (
        <div className="space-y-6">
          <button onClick={() => setResult(null)} className="text-sm text-muted hover:text-foreground">New Design</button>

          <div className="bg-card-bg border border-card-border rounded-xl p-5">
            <h2 className="text-lg font-bold mb-3 gradient-text">Research Question</h2>
            <p className="text-sm">{result.research_question}</p>
          </div>

          {result.pico && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {["population", "intervention", "comparison", "outcome"].map((key) => (
                <div key={key} className="bg-card-bg border border-card-border rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-accent uppercase mb-2">{key}</h3>
                  <p className="text-sm text-muted">{result.pico[key]}</p>
                </div>
              ))}
            </div>
          )}

          {result.suggested_datasets && (
            <div className="bg-card-bg border border-card-border rounded-xl p-5">
              <h3 className="font-semibold mb-2">Suggested Datasets</h3>
              {result.suggested_datasets.map((d: any, i: number) => (
                <p key={i} className="text-sm text-muted">&bull; {d.name} ({d.size}) — {d.modality}</p>
              ))}
            </div>
          )}

          {result.model_architecture && (
            <div className="bg-card-bg border border-card-border rounded-xl p-5">
              <h3 className="font-semibold mb-2">Model Architecture</h3>
              <p className="text-sm text-muted">{result.model_architecture}</p>
              {result.architecture_justification && <p className="text-xs text-zinc-500 mt-1">{result.architecture_justification}</p>}
            </div>
          )}

          {result.expected_challenges && (
            <div className="bg-card-bg border border-card-border rounded-xl p-5">
              <h3 className="font-semibold mb-2">Expected Challenges</h3>
              {result.expected_challenges.map((c: string, i: number) => (
                <p key={i} className="text-sm text-muted">&bull; {c}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

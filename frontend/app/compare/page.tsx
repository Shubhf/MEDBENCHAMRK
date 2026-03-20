"use client";

import { useEffect, useState } from "react";
import * as api from "@/lib/api";

export default function ComparePage() {
  const [papers, setPapers] = useState<any[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [table, setTable] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.papers.list().then((d) => setPapers(d.papers)).catch(() => {}); }, []);

  const toggle = (id: string) => setSelected((p) => p.includes(id) ? p.filter((x) => x !== id) : [...p, id]);

  const generate = async () => {
    if (selected.length < 2) return;
    setLoading(true);
    try {
      const result = await api.compare.generate(selected);
      setTable(result);
    } catch (err: any) { alert(err.message); }
    setLoading(false);
  };

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">
      <a href="/dashboard" className="text-accent text-sm mb-4 inline-block">&larr; Dashboard</a>
      <h1 className="text-2xl font-bold mb-6">Medical Comparison Table</h1>

      {!table && (
        <>
          <div className="space-y-2 mb-6 max-h-60 overflow-y-auto">
            {papers.map((p) => (
              <label key={p.id} className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer ${
                selected.includes(p.id) ? "bg-accent/10 border-accent" : "bg-card-bg border-card-border"
              }`}>
                <input type="checkbox" checked={selected.includes(p.id)} onChange={() => toggle(p.id)} />
                <span className="text-sm">{p.title}</span>
              </label>
            ))}
          </div>
          <button onClick={generate} disabled={loading || selected.length < 2}
            className="px-8 py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-lg disabled:opacity-50">
            {loading ? "Generating..." : "Generate Comparison"}
          </button>
        </>
      )}

      {table && (
        <div className="overflow-x-auto">
          <button onClick={() => setTable(null)} className="text-sm text-muted hover:text-foreground mb-4">New Comparison</button>
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr>
                {(table.columns || []).map((col: string) => (
                  <th key={col} className="text-left p-3 border-b border-card-border text-muted font-medium">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(table.rows || []).map((row: any, i: number) => (
                <tr key={i} className="hover:bg-card-bg/50">
                  {(table.columns || []).map((col: string) => (
                    <td key={col} className="p-3 border-b border-card-border">{row[col] || "N/A"}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

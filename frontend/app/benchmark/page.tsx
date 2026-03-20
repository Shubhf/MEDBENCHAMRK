"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function BenchmarkPage() {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    fetch("/api/benchmark/leaderboard").then((r) => r.json()).then((d) => setLeaderboard(d.leaderboard || [])).catch(() => {});
  }, []);

  const chartData = [
    { task: "Gap ID", ...Object.fromEntries(leaderboard.map((m) => [m.model, (m.gap_identification * 100).toFixed(0)])) },
    { task: "Anti-Halluc.", ...Object.fromEntries(leaderboard.map((m) => [m.model, ((1 - m.hallucination_rate) * 100).toFixed(0)])) },
    { task: "Entity Ext.", ...Object.fromEntries(leaderboard.map((m) => [m.model, (m.entity_extraction * 100).toFixed(0)])) },
    { task: "PICO", ...Object.fromEntries(leaderboard.map((m) => [m.model, (m.pico_design * 20).toFixed(0)])) },
    { task: "Clinical", ...Object.fromEntries(leaderboard.map((m) => [m.model, (m.clinical_relevance * 100).toFixed(0)])) },
  ];

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <a href="/dashboard" className="text-accent text-sm mb-4 inline-block">&larr; Dashboard</a>
      <h1 className="text-2xl font-bold mb-2">MedResearchBench</h1>
      <p className="text-muted mb-8">Open benchmark for medical AI research intelligence tools</p>

      <div className="bg-card-bg border border-card-border rounded-xl p-6 mb-8">
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData}>
            <XAxis dataKey="task" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
            <YAxis tick={{ fill: "#a1a1aa", fontSize: 12 }} />
            <Tooltip contentStyle={{ backgroundColor: "#141414", border: "1px solid #27272a", borderRadius: 8 }} />
            <Legend />
            {leaderboard.map((m, i) => {
              const colors = ["#0ea5e9", "#6366f1", "#f59e0b", "#10b981", "#ef4444"];
              return <Bar key={m.model} dataKey={m.model} fill={colors[i % colors.length]} radius={[4, 4, 0, 0]} />;
            })}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="text-left text-muted">
              <th className="p-3 border-b border-card-border">Model</th>
              <th className="p-3 border-b border-card-border">Gap ID</th>
              <th className="p-3 border-b border-card-border">Halluc. Rate</th>
              <th className="p-3 border-b border-card-border">Entity F1</th>
              <th className="p-3 border-b border-card-border">PICO (1-5)</th>
              <th className="p-3 border-b border-card-border">Clinical Rel.</th>
              <th className="p-3 border-b border-card-border font-bold">Overall</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((m, i) => (
              <tr key={m.model} className={i === 0 ? "text-accent font-medium" : ""}>
                <td className="p-3 border-b border-card-border font-semibold">{m.model}</td>
                <td className="p-3 border-b border-card-border">{(m.gap_identification * 100).toFixed(0)}%</td>
                <td className="p-3 border-b border-card-border">{(m.hallucination_rate * 100).toFixed(0)}%</td>
                <td className="p-3 border-b border-card-border">{(m.entity_extraction * 100).toFixed(0)}%</td>
                <td className="p-3 border-b border-card-border">{m.pico_design.toFixed(1)}</td>
                <td className="p-3 border-b border-card-border">{(m.clinical_relevance * 100).toFixed(0)}%</td>
                <td className="p-3 border-b border-card-border font-bold">{(m.overall * 100).toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

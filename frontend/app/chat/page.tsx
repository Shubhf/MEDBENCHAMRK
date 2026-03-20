"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import * as api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: any[];
  confidence?: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim() || loading) return;
    const query = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setLoading(true);

    try {
      const result = await api.qa.ask(query);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          citations: result.citations,
          confidence: result.confidence,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${err.message}` }]);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col max-w-4xl mx-auto p-6">
      <a href="/dashboard" className="text-accent text-sm mb-4">&larr; Dashboard</a>
      <h1 className="text-2xl font-bold mb-6">Medical AI Q&A</h1>

      <div className="flex-1 space-y-4 mb-6 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted text-lg mb-2">Ask questions about your medical AI papers</p>
            <p className="text-zinc-600 text-sm">Every answer cites paper + section + page. No hallucinations.</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-xl p-4 ${
              m.role === "user" ? "bg-accent text-white" : "bg-card-bg border border-card-border"
            }`}>
              <p className="text-sm whitespace-pre-wrap">{m.content}</p>
              {m.confidence !== undefined && (
                <p className="text-xs mt-2 opacity-60">Confidence: {(m.confidence * 100).toFixed(0)}%</p>
              )}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-zinc-700/50">
                  <p className="text-xs text-muted mb-1">Citations:</p>
                  {m.citations.map((c: any, j: number) => (
                    <p key={j} className="text-xs text-zinc-400">[{j + 1}] {c.paper_title} — {c.section}{c.page ? `, p.${c.page}` : ""}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-card-bg border border-card-border rounded-xl p-4">
              <div className="flex gap-1"><span className="animate-pulse">.</span><span className="animate-pulse delay-100">.</span><span className="animate-pulse delay-200">.</span></div>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <input
          type="text" value={input} onChange={(e) => setInput(e.target.value)}
          placeholder="Which papers achieve >90% AUC on diabetic retinopathy?"
          className="flex-1 px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent"
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button onClick={send} disabled={loading}
          className="p-3 bg-accent hover:bg-accent-dark text-white rounded-lg transition-colors disabled:opacity-50">
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

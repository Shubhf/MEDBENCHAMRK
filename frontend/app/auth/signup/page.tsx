"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";

const FOCUS_OPTIONS = [
  "Retinal Imaging", "Brain Tumor", "Radiology AI", "Pathology AI",
  "Dermatology AI", "Cardiology AI", "Ophthalmology", "Ultrasound AI",
  "Medical NLP", "Drug Discovery", "Federated Learning", "Other",
];

export default function SignupPage() {
  const [form, setForm] = useState({
    email: "", password: "", full_name: "", institution: "",
    research_focus: [] as string[], clinical_background: false,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const toggleFocus = (f: string) => {
    setForm((prev) => ({
      ...prev,
      research_focus: prev.research_focus.includes(f)
        ? prev.research_focus.filter((x) => x !== f)
        : [...prev.research_focus, f],
    }));
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Signup failed");
      if (data.session) {
        await supabase.auth.setSession({ access_token: data.session, refresh_token: "" });
      }
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold mb-2 text-center">Create your account</h1>
        <p className="text-muted text-center mb-8 text-sm">Join medical AI researchers using MedResearch Mind</p>
        <form onSubmit={handleSignup} className="space-y-4">
          <input type="text" required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            placeholder="Full name" className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent" />
          <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="Email" className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent" />
          <input type="password" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="Password (min 6 chars)" className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent" />
          <input type="text" value={form.institution} onChange={(e) => setForm({ ...form, institution: e.target.value })}
            placeholder="Institution" className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:outline-none focus:border-accent" />
          <div>
            <p className="text-sm text-muted mb-2">Research focus (select all that apply)</p>
            <div className="flex flex-wrap gap-2">
              {FOCUS_OPTIONS.map((f) => (
                <button key={f} type="button" onClick={() => toggleFocus(f)}
                  className={`px-3 py-1.5 text-xs rounded-full border transition-colors ${
                    form.research_focus.includes(f) ? "bg-accent/20 border-accent text-accent" : "border-card-border text-muted hover:border-zinc-500"
                  }`}>
                  {f}
                </button>
              ))}
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-muted">
            <input type="checkbox" checked={form.clinical_background} onChange={(e) => setForm({ ...form, clinical_background: e.target.checked })}
              className="rounded" />
            I have a clinical background (MD, radiology, etc.)
          </label>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-lg transition-colors disabled:opacity-50">
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>
        <p className="text-center text-sm text-muted mt-6">
          Already have an account? <a href="/auth/login" className="text-accent hover:underline">Sign in</a>
        </p>
      </div>
    </div>
  );
}

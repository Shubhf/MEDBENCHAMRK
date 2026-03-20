"use client";

import { useState } from "react";
import { motion } from "framer-motion";

export default function EmailCapture() {
  const [email, setEmail] = useState("");
  const [institution, setInstitution] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    try {
      await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, institution }),
      });
      setSubmitted(true);
    } catch {
      // Silent fail
    }
    setLoading(false);
  };

  return (
    <section className="py-20 px-4 bg-card-bg/30">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="max-w-xl mx-auto text-center"
      >
        <h2 className="text-2xl md:text-3xl font-bold mb-4">
          Join medical AI researchers getting early access
        </h2>

        {submitted ? (
          <p className="text-accent font-medium text-lg">
            You&apos;re on the list! We&apos;ll be in touch soon.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 mt-6">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Your email"
              className="flex-1 px-4 py-3 bg-card-bg border border-card-border rounded-lg text-foreground placeholder:text-zinc-500 focus:outline-none focus:border-accent"
            />
            <input
              type="text"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              placeholder="Institution"
              className="flex-1 px-4 py-3 bg-card-bg border border-card-border rounded-lg text-foreground placeholder:text-zinc-500 focus:outline-none focus:border-accent"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? "..." : "Get Access"}
            </button>
          </form>
        )}
      </motion.div>
    </section>
  );
}

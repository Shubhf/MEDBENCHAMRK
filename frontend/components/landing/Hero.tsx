"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

const placeholders = [
  "Paste a PubMed link...",
  "Drop a MICCAI talk URL...",
  "Upload your retinal imaging papers...",
  "Enter a clinical AI problem...",
];

export default function Hero() {
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIdx((i) => (i + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative overflow-hidden px-4 pt-24 pb-20 md:pt-32 md:pb-28">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-accent/5 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-accent/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6"
        >
          The Research Brain for{" "}
          <span className="gradient-text">Medical AI</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Drop PubMed studies, ArXiv papers, MICCAI talks, or GitHub repos.
          Find research gaps nobody has solved. Design your next study.
          Built with deep medical AI domain knowledge.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="max-w-xl mx-auto mb-8"
        >
          <div className="relative glow-border rounded-xl">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={placeholders[placeholderIdx]}
              className="w-full px-6 py-4 bg-card-bg border border-card-border rounded-xl text-foreground placeholder:text-zinc-500 focus:outline-none focus:border-accent transition-colors text-lg"
            />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.45 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="/dashboard"
            className="px-8 py-4 bg-accent hover:bg-accent-dark text-white font-semibold rounded-xl transition-colors text-lg"
          >
            Find Gaps Free — No credit card
          </a>
          <a
            href="/benchmark"
            className="text-accent hover:text-accent-dark transition-colors font-medium"
          >
            See MedResearchBench &rarr;
          </a>
        </motion.div>
      </div>
    </section>
  );
}

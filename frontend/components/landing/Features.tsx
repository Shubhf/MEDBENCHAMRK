"use client";

import { motion } from "framer-motion";
import {
  Search,
  FileText,
  Shield,
  FlaskConical,
  Brain,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Medical Gap Finder",
    description:
      "Understands imaging modalities, clinical datasets, and medical constraints. Finds gaps that matter clinically — not just statistically.",
  },
  {
    icon: FileText,
    title: "Works With Medical Sources",
    description:
      "PubMed, ArXiv, bioRxiv, MICCAI talks, ClinicalTrials.gov, GitHub medical repos. Every source type medical AI researchers use.",
  },
  {
    icon: Shield,
    title: "Zero Hallucination Q&A",
    description:
      "Especially critical in medical AI. Every answer cites paper + section + page. Confidence scores on every response. No fabricated clinical claims. Ever.",
  },
  {
    icon: FlaskConical,
    title: "PICO Experiment Designer",
    description:
      "Gap found \u2192 experiment designed in PICO format. Population. Intervention. Comparison. Outcome. The way clinician researchers think.",
  },
  {
    icon: Brain,
    title: "Medical Knowledge Memory",
    description:
      "Remembers your clinical focus area. Tracks which modalities and conditions you study. Gets smarter every session.",
  },
  {
    icon: BarChart3,
    title: "MedResearchBench",
    description:
      "Open benchmark for medical AI research tools. The standard every medical AI lab references.",
  },
];

export default function Features() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Built for <span className="gradient-text">Medical AI Researchers</span>
        </h2>
        <p className="text-center text-muted mb-14 max-w-2xl mx-auto">
          Every feature designed with clinical awareness and medical domain
          knowledge.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 bg-card-bg border border-card-border rounded-xl glow-border transition-all hover:-translate-y-1"
            >
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <f.icon className="w-5 h-5 text-accent" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-muted leading-relaxed">
                {f.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

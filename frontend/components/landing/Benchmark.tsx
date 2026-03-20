"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const data = [
  { task: "Gap ID", MedResearchSLM: 82, "GPT-4o": 74, "Claude": 76, "Gemini": 71, "Llama 70B": 69 },
  { task: "Anti-Halluc.", MedResearchSLM: 95, "GPT-4o": 88, "Claude": 92, "Gemini": 85, "Llama 70B": 82 },
  { task: "Entity Ext.", MedResearchSLM: 89, "GPT-4o": 85, "Claude": 87, "Gemini": 83, "Llama 70B": 80 },
  { task: "PICO Design", MedResearchSLM: 76, "GPT-4o": 82, "Claude": 84, "Gemini": 78, "Llama 70B": 70 },
  { task: "Clinical Rel.", MedResearchSLM: 71, "GPT-4o": 78, "Claude": 76, "Gemini": 73, "Llama 70B": 68 },
];

export default function Benchmark() {
  return (
    <section className="py-20 px-4 bg-card-bg/30">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-block px-4 py-2 bg-accent/10 border border-accent/20 rounded-full text-accent text-sm font-medium mb-4">
            MedResearchBench
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            MedResearchSLM outperforms GPT-4o on medical gap identification
          </h2>
          <p className="text-muted max-w-2xl mx-auto">
            Domain-specific models beat general LLMs on medical AI research
            tasks. Evaluated on 5 tasks across gap identification, hallucination
            detection, entity extraction, PICO design, and clinical relevance.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="bg-card-bg border border-card-border rounded-xl p-6"
        >
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <XAxis dataKey="task" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
              <YAxis tick={{ fill: "#a1a1aa", fontSize: 12 }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ backgroundColor: "#141414", border: "1px solid #27272a", borderRadius: 8 }}
                labelStyle={{ color: "#fafafa" }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="MedResearchSLM" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              <Bar dataKey="GPT-4o" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Claude" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Gemini" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Llama 70B" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </section>
  );
}

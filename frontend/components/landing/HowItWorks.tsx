"use client";

import { motion } from "framer-motion";

const steps = [
  {
    num: "1",
    title: "Add your sources",
    description:
      "PubMed links, ArXiv papers, conference talks, GitHub repos. Anything medical AI related.",
  },
  {
    num: "2",
    title: "Find what\u2019s missing",
    description:
      "Click \u2018Find Gaps\u2019. AI analyzes your collection with clinical and technical awareness.",
  },
  {
    num: "3",
    title: "Design your next study",
    description:
      "Ranked gaps + PICO experiment proposals + citations. Ready for your next grant or paper.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-14">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <motion.div
              key={step.num}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="text-center"
            >
              <div className="w-12 h-12 rounded-full bg-accent text-white font-bold text-xl flex items-center justify-center mx-auto mb-4">
                {step.num}
              </div>
              <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
              <p className="text-sm text-muted leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

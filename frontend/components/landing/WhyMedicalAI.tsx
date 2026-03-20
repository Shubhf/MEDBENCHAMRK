"use client";

import { motion } from "framer-motion";

export default function WhyMedicalAI() {
  return (
    <section className="py-20 px-4 bg-card-bg/30">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="max-w-3xl mx-auto text-center"
      >
        <h2 className="text-3xl md:text-4xl font-bold mb-8">
          Why <span className="gradient-text">Medical AI</span> Specifically?
        </h2>
        <p className="text-lg text-muted leading-relaxed mb-6">
          Generic AI tools don&apos;t understand the difference between Dice
          score and AUC. They don&apos;t know MIMIC-III from DRIVE. They
          can&apos;t design a PICO-formatted experiment.
        </p>
        <p className="text-lg text-foreground leading-relaxed font-medium">
          MedResearch Mind was built with deep medical AI domain expertise.
          That difference shows in every gap it finds.
        </p>
      </motion.div>
    </section>
  );
}

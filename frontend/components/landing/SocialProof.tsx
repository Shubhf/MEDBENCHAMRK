"use client";

import { motion } from "framer-motion";

export default function SocialProof() {
  return (
    <section className="border-y border-card-border bg-card-bg/50 py-6 px-4">
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="max-w-5xl mx-auto text-center"
      >
        <p className="text-sm md:text-base text-muted">
          Built by medical AI researchers &nbsp;|&nbsp; Trusted by labs and PhD students worldwide
        </p>
      </motion.div>
    </section>
  );
}

"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for PhD students",
    features: [
      "10 papers/links",
      "20 queries/month",
      "Basic gap finder",
      "Community support",
    ],
    cta: "Start Free",
    popular: false,
  },
  {
    name: "Pro",
    price: "$9",
    period: "/month",
    description: "For serious researchers",
    features: [
      "100 papers/links",
      "Unlimited queries",
      "Full gap reports (PDF)",
      "PICO experiment designer",
      "Session memory",
      "Priority processing",
    ],
    cta: "Start Pro",
    popular: true,
  },
  {
    name: "Lab",
    price: "$29",
    period: "/month",
    description: "For research labs",
    features: [
      "Unlimited everything",
      "Team workspace (5 seats)",
      "API access",
      "MedResearchBench API",
      "Priority processing",
      "Dedicated support",
    ],
    cta: "Start Lab Trial",
    popular: false,
  },
];

export default function Pricing() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
          Simple Pricing
        </h2>
        <p className="text-center text-muted mb-14">
          Free to start. Scale when you need more.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={`relative p-6 rounded-xl border transition-all hover:-translate-y-1 ${
                plan.popular
                  ? "bg-card-bg border-accent glow-border"
                  : "bg-card-bg border-card-border"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-accent text-white text-xs font-semibold rounded-full">
                  MOST POPULAR
                </div>
              )}
              <h3 className="text-xl font-bold mb-1">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-3xl font-extrabold">{plan.price}</span>
                <span className="text-muted text-sm">{plan.period}</span>
              </div>
              <p className="text-sm text-muted mb-6">{plan.description}</p>
              <ul className="space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <Check className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <a
                href="/dashboard"
                className={`block w-full text-center py-3 rounded-lg font-semibold transition-colors ${
                  plan.popular
                    ? "bg-accent hover:bg-accent-dark text-white"
                    : "bg-zinc-800 hover:bg-zinc-700 text-foreground"
                }`}
              >
                {plan.cta}
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

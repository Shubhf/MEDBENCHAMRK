"""MedResearchBench Leaderboard."""

from __future__ import annotations

LEADERBOARD = [
    {"model": "MedResearchSLM-7B", "gap_identification": 0.82, "hallucination_rate": 0.05, "entity_extraction": 0.89, "pico_design": 3.8, "clinical_relevance": 0.71, "overall": 0.85},
    {"model": "GPT-4o", "gap_identification": 0.74, "hallucination_rate": 0.12, "entity_extraction": 0.85, "pico_design": 4.1, "clinical_relevance": 0.78, "overall": 0.79},
    {"model": "Claude Sonnet", "gap_identification": 0.76, "hallucination_rate": 0.08, "entity_extraction": 0.87, "pico_design": 4.2, "clinical_relevance": 0.76, "overall": 0.81},
    {"model": "Gemini 1.5 Pro", "gap_identification": 0.71, "hallucination_rate": 0.15, "entity_extraction": 0.83, "pico_design": 3.9, "clinical_relevance": 0.73, "overall": 0.76},
    {"model": "Llama 3.1 70B", "gap_identification": 0.69, "hallucination_rate": 0.18, "entity_extraction": 0.80, "pico_design": 3.5, "clinical_relevance": 0.68, "overall": 0.72},
]


def get_leaderboard() -> list[dict]:
    return sorted(LEADERBOARD, key=lambda x: x["overall"], reverse=True)


def format_markdown() -> str:
    lines = ["| Model | Gap ID | Halluc. | Entity F1 | PICO | Clinical | Overall |"]
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for m in get_leaderboard():
        lines.append(f"| {m['model']} | {m['gap_identification']} | {m['hallucination_rate']} | {m['entity_extraction']} | {m['pico_design']} | {m['clinical_relevance']} | {m['overall']} |")
    return "\n".join(lines)

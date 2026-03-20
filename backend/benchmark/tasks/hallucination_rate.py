"""Hallucination Rate Task — Are citations real? Are claims accurate?"""

from __future__ import annotations

import re


class HallucinationRateTask:
    """Evaluate hallucination rate in medical AI Q&A."""

    name = "hallucination_rate"
    metric = "Hallucination %"

    def detect_hallucinations(self, answer: str, source_papers: list[dict]) -> list[dict]:
        """Check for fabricated citations or unsupported claims."""
        hallucinations = []
        paper_titles = {p["title"].lower() for p in source_papers}

        # Check cited papers exist
        cited = re.findall(r'"([^"]+)"', answer) + re.findall(r"\(([^)]+,\s*\d{4})\)", answer)
        for cite in cited:
            cite_lower = cite.lower()
            if not any(t in cite_lower or cite_lower in t for t in paper_titles):
                hallucinations.append({"type": "fabricated_citation", "text": cite})

        # Check for unsupported numerical claims
        numbers = re.findall(r"(\d+\.?\d*)\s*%", answer)
        for num in numbers:
            # Flag any percentage claim not found in source text
            source_text = " ".join(p.get("abstract", "") for p in source_papers).lower()
            if num not in source_text:
                hallucinations.append({"type": "unsupported_statistic", "text": f"{num}%"})

        return hallucinations

    def evaluate(self, model_answers: list[dict], source_papers: list[dict]) -> dict[str, float]:
        """Compute hallucination rate across multiple answers."""
        total_claims = 0
        hallucinated = 0

        for answer_data in model_answers:
            answer = answer_data.get("answer", "")
            hallucs = self.detect_hallucinations(answer, source_papers)
            cited = re.findall(r'"([^"]+)"', answer)
            total_claims += max(len(cited), 1)
            hallucinated += len(hallucs)

        rate = hallucinated / total_claims if total_claims else 0
        return {"hallucination_rate": round(rate, 3), "total_claims": total_claims, "hallucinated": hallucinated}

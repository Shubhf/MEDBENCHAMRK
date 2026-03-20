"""Clinical Relevance Task — Assess clinical translation potential."""

from __future__ import annotations

import math


class ClinicalRelevanceTask:
    """Evaluate clinical relevance assessment accuracy."""

    name = "clinical_relevance"
    metric = "Correlation with expert scores"

    def evaluate(self, model_ratings: list[float], expert_ratings: list[float]) -> dict[str, float]:
        """Compute Pearson correlation between model and expert ratings."""
        if len(model_ratings) != len(expert_ratings) or len(model_ratings) < 2:
            return {"correlation": 0.0, "mae": 0.0, "n": len(model_ratings)}

        n = len(model_ratings)
        mean_m = sum(model_ratings) / n
        mean_e = sum(expert_ratings) / n

        cov = sum((m - mean_m) * (e - mean_e) for m, e in zip(model_ratings, expert_ratings)) / n
        std_m = math.sqrt(sum((m - mean_m) ** 2 for m in model_ratings) / n)
        std_e = math.sqrt(sum((e - mean_e) ** 2 for e in expert_ratings) / n)

        correlation = cov / (std_m * std_e) if (std_m * std_e) > 0 else 0
        mae = sum(abs(m - e) for m, e in zip(model_ratings, expert_ratings)) / n

        return {"correlation": round(correlation, 3), "mae": round(mae, 3), "n": n}

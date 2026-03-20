"""PICO Design Task — Generate quality experiment proposals."""

from __future__ import annotations


class PICODesignTask:
    """Evaluate PICO-formatted experiment design quality."""

    name = "pico_design"
    metric = "Expert score (1-5)"

    REQUIRED_FIELDS = ["population", "intervention", "comparison", "outcome"]

    def evaluate(self, pico_output: dict) -> dict[str, float]:
        """Score PICO proposal on completeness, specificity, and feasibility."""
        scores = {}

        # Completeness (are all PICO fields present and non-empty?)
        present = sum(1 for f in self.REQUIRED_FIELDS if pico_output.get("pico", {}).get(f))
        scores["completeness"] = round(present / len(self.REQUIRED_FIELDS) * 5, 1)

        # Specificity (are fields detailed enough?)
        specificity = 0
        for f in self.REQUIRED_FIELDS:
            text = pico_output.get("pico", {}).get(f, "")
            if len(text) > 50:
                specificity += 1.25
            elif len(text) > 20:
                specificity += 0.75
        scores["specificity"] = round(min(specificity, 5), 1)

        # Feasibility (does it include datasets, compute, challenges?)
        feas = 0
        if pico_output.get("suggested_datasets"):
            feas += 1.5
        if pico_output.get("model_architecture"):
            feas += 1.0
        if pico_output.get("compute_estimate"):
            feas += 1.0
        if pico_output.get("expected_challenges"):
            feas += 1.5
        scores["feasibility"] = round(min(feas, 5), 1)

        scores["overall"] = round((scores["completeness"] + scores["specificity"] + scores["feasibility"]) / 3, 1)
        return scores

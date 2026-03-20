"""Benchmark Evaluator — run all tasks and compare models."""

from __future__ import annotations

from backend.benchmark.tasks.gap_identification import GapIdentificationTask
from backend.benchmark.tasks.hallucination_rate import HallucinationRateTask
from backend.benchmark.tasks.entity_extraction import EntityExtractionTask
from backend.benchmark.tasks.pico_design import PICODesignTask
from backend.benchmark.tasks.clinical_relevance import ClinicalRelevanceTask


class BenchmarkEvaluator:
    """Run MedResearchBench evaluation suite."""

    def __init__(self) -> None:
        self.tasks = {
            "gap_identification": GapIdentificationTask(),
            "hallucination_rate": HallucinationRateTask(),
            "entity_extraction": EntityExtractionTask(),
            "pico_design": PICODesignTask(),
            "clinical_relevance": ClinicalRelevanceTask(),
        }

    def run_all(self, model_name: str, outputs: dict) -> dict:
        """Run all benchmark tasks and return results."""
        results = {"model": model_name, "tasks": {}}

        for task_name, task in self.tasks.items():
            if task_name in outputs:
                task_output = outputs[task_name]
                score = task.evaluate(**task_output)
                results["tasks"][task_name] = score

        return results

    def compare_models(self, all_results: list[dict]) -> str:
        """Generate a markdown comparison table."""
        if not all_results:
            return "No results to compare."

        tasks = list(all_results[0].get("tasks", {}).keys())
        lines = ["| Model | " + " | ".join(tasks) + " |"]
        lines.append("| --- | " + " | ".join(["---"] * len(tasks)) + " |")

        for r in all_results:
            model = r["model"]
            scores = []
            for t in tasks:
                task_scores = r.get("tasks", {}).get(t, {})
                main_score = list(task_scores.values())[0] if task_scores else "N/A"
                scores.append(str(main_score))
            lines.append(f"| {model} | " + " | ".join(scores) + " |")

        return "\n".join(lines)

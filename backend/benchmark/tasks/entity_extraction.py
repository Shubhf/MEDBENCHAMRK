"""Entity Extraction Task — Extract medical entities from paper text."""

from __future__ import annotations


class EntityExtractionTask:
    """Evaluate medical entity extraction quality."""

    name = "entity_extraction"
    metric = "F1 per entity type"

    ENTITY_TYPES = ["imaging_modality", "anatomy", "condition", "architecture", "dataset", "metric", "technique"]

    def evaluate(self, extracted: dict[str, list[str]], ground_truth: dict[str, list[str]]) -> dict[str, float]:
        """Compute per-type F1 scores."""
        results = {}
        total_f1 = 0
        count = 0

        for entity_type in self.ENTITY_TYPES:
            pred = set(e.lower() for e in extracted.get(entity_type, []))
            gt = set(e.lower() for e in ground_truth.get(entity_type, []))

            if not gt and not pred:
                continue

            tp = len(pred & gt)
            precision = tp / len(pred) if pred else 0
            recall = tp / len(gt) if gt else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

            results[f"{entity_type}_f1"] = round(f1, 3)
            results[f"{entity_type}_precision"] = round(precision, 3)
            results[f"{entity_type}_recall"] = round(recall, 3)
            total_f1 += f1
            count += 1

        results["macro_f1"] = round(total_f1 / count, 3) if count else 0
        return results

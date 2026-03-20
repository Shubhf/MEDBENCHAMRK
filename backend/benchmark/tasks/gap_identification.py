"""Gap Identification Task — Can the model find real research gaps?"""

from __future__ import annotations

from typing import Any


class GapIdentificationTask:
    """Evaluate a model's ability to identify medical AI research gaps."""

    name = "gap_identification"
    metric = "Recall@5, Precision@5"

    def generate_test_cases(self) -> list[dict]:
        """Return sample test cases (in production, load from HuggingFace)."""
        return [
            {
                "id": "gap_001",
                "topic": "retinal_vessel_segmentation",
                "input_papers": [
                    {"title": "U-Net for Retinal Vessel Segmentation", "modality": "fundus", "architecture": "U-Net", "dataset": "DRIVE", "year": 2020},
                    {"title": "ResNet-based DR Grading", "modality": "fundus", "architecture": "ResNet50", "dataset": "EyePACS", "year": 2021},
                ],
                "ground_truth_gaps": [
                    "No transformer-based approaches",
                    "No OCT modality explored",
                    "No pediatric population",
                    "No federated learning approaches",
                    "No multi-center validation",
                ],
            },
        ]

    def evaluate(self, model_output: list[str], ground_truth: list[str], k: int = 5) -> dict[str, float]:
        """Compute Recall@K and Precision@K."""
        model_top_k = model_output[:k]
        gt_set = set(g.lower() for g in ground_truth)

        hits = 0
        for pred in model_top_k:
            pred_lower = pred.lower()
            for gt in gt_set:
                if gt in pred_lower or pred_lower in gt:
                    hits += 1
                    break

        recall = hits / len(gt_set) if gt_set else 0
        precision = hits / len(model_top_k) if model_top_k else 0

        return {"recall_at_k": round(recall, 3), "precision_at_k": round(precision, 3), "k": k}

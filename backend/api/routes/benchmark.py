"""MedResearchBench routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

LEADERBOARD = [
    {
        "model": "MedResearchSLM-7B",
        "gap_identification": 0.82,
        "hallucination_rate": 0.05,
        "entity_extraction": 0.89,
        "pico_design": 3.8,
        "clinical_relevance": 0.71,
        "overall": 0.85,
    },
    {
        "model": "GPT-4o",
        "gap_identification": 0.74,
        "hallucination_rate": 0.12,
        "entity_extraction": 0.85,
        "pico_design": 4.1,
        "clinical_relevance": 0.78,
        "overall": 0.79,
    },
    {
        "model": "Claude Sonnet",
        "gap_identification": 0.76,
        "hallucination_rate": 0.08,
        "entity_extraction": 0.87,
        "pico_design": 4.2,
        "clinical_relevance": 0.76,
        "overall": 0.81,
    },
    {
        "model": "Gemini 1.5 Pro",
        "gap_identification": 0.71,
        "hallucination_rate": 0.15,
        "entity_extraction": 0.83,
        "pico_design": 3.9,
        "clinical_relevance": 0.73,
        "overall": 0.76,
    },
    {
        "model": "Llama 3.1 70B",
        "gap_identification": 0.69,
        "hallucination_rate": 0.18,
        "entity_extraction": 0.80,
        "pico_design": 3.5,
        "clinical_relevance": 0.68,
        "overall": 0.72,
    },
]

TASKS = [
    {"name": "Gap Identification", "metric": "Recall@5 / Precision@5", "description": "Identify research gaps from 10 papers on the same condition"},
    {"name": "Hallucination Rate", "metric": "Hallucination %", "description": "Rate of fabricated citations or clinical claims"},
    {"name": "Entity Extraction", "metric": "F1 per entity type", "description": "Extract medical entities from paper text"},
    {"name": "PICO Design", "metric": "Expert score (1-5)", "description": "Generate PICO-formatted experiment proposals"},
    {"name": "Clinical Relevance", "metric": "Correlation with experts", "description": "Assess clinical translation potential"},
]


@router.get("/leaderboard")
async def get_leaderboard():
    return {"leaderboard": LEADERBOARD}


@router.get("/tasks")
async def get_tasks():
    return {"tasks": TASKS}

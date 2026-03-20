"""Gap analysis routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.api.deps import get_current_user, get_llm_router
from backend.agents.gap_finder import MedicalGapFinder
from backend.db import supabase as db

router = APIRouter()


class AnalyzeRequest(BaseModel):
    source_ids: list[str]


class FeedbackRequest(BaseModel):
    gap_index: int
    outcome: str  # accepted, rejected, modified
    modification: str = ""


@router.post("/analyze")
async def analyze_gaps(req: AnalyzeRequest, user: dict = Depends(get_current_user)):
    """Run gap analysis on selected papers."""
    if len(req.source_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 papers for gap analysis")

    finder = MedicalGapFinder(llm=get_llm_router())
    try:
        report = await finder.analyze(req.source_ids, user["id"])
        return {
            "id": report.id,
            "clinical_topic": report.clinical_topic,
            "gaps": [finder._gap_to_dict(g) for g in report.gaps],
            "experiment_proposals": report.experiment_proposals,
            "summary": report.summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def list_reports(user: dict = Depends(get_current_user)):
    reports = db.select("gap_reports", filters={"user_id": user["id"]}, order="-created_at", service=True)
    return {"reports": reports}


@router.get("/reports/{report_id}")
async def get_report(report_id: str, user: dict = Depends(get_current_user)):
    results = db.select("gap_reports", filters={"id": report_id, "user_id": user["id"]}, service=True)
    if not results:
        raise HTTPException(status_code=404, detail="Report not found")
    return results[0]


@router.post("/reports/{report_id}/feedback")
async def feedback(report_id: str, req: FeedbackRequest, user: dict = Depends(get_current_user)):
    """Record feedback on a gap — TRAINING DATA."""
    finder = MedicalGapFinder(llm=get_llm_router())
    await finder.feedback(report_id, req.gap_index, req.outcome, req.modification)
    return {"success": True}

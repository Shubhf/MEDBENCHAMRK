"""Comparison table routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel

from backend.api.deps import get_current_user, get_llm_router
from backend.agents.comparison_agent import ComparisonAgent
from backend.db import supabase as db

router = APIRouter()


class CompareRequest(BaseModel):
    source_ids: list[str]


@router.post("/generate")
async def generate_comparison(req: CompareRequest, user: dict = Depends(get_current_user)):
    agent = ComparisonAgent(llm=get_llm_router())
    result = await agent.generate(req.source_ids, user["id"])
    return result


@router.get("/{comparison_id}")
async def get_comparison(comparison_id: str, user: dict = Depends(get_current_user)):
    results = db.select("comparisons", filters={"id": comparison_id, "user_id": user["id"]})
    if not results:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return results[0]


@router.get("/{comparison_id}/csv")
async def export_csv(comparison_id: str, user: dict = Depends(get_current_user)):
    results = db.select("comparisons", filters={"id": comparison_id, "user_id": user["id"]})
    if not results:
        raise HTTPException(status_code=404, detail="Comparison not found")
    agent = ComparisonAgent()
    csv_content = agent.export_csv(results[0].get("table_data", []))
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=comparison.csv"})

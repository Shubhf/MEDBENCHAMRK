"""PICO Experiment Designer routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.api.deps import get_current_user, get_llm_router
from backend.agents.experiment_designer import ExperimentDesigner

router = APIRouter()


class DesignRequest(BaseModel):
    gap_description: str
    context: str = ""


@router.post("/design")
async def design_experiment(req: DesignRequest, user: dict = Depends(get_current_user)):
    designer = ExperimentDesigner(llm=get_llm_router())
    result = await designer.design(req.gap_description, req.context, user["id"])
    return result


@router.get("/history")
async def experiment_history(user: dict = Depends(get_current_user)):
    designer = ExperimentDesigner()
    history = designer.get_history(user["id"])
    return {"experiments": history}


@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str, user: dict = Depends(get_current_user)):
    from backend.db import supabase as db
    results = db.select("experiments", filters={"id": experiment_id, "user_id": user["id"]}, service=True)
    if not results:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return results[0]

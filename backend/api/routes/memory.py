"""Memory routes — sessions, knowledge graph, patterns."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.deps import get_current_user, get_memory_manager

router = APIRouter()


class StartSessionRequest(BaseModel):
    session_name: str = ""
    clinical_focus: str = ""


class EndSessionRequest(BaseModel):
    summary: str = ""


@router.get("/welcome")
async def get_welcome(user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    return {"message": mm.get_session_welcome(user["id"])}


@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    sessions = mm.episodic.get_recent_sessions(user["id"], limit=20)
    return {"sessions": sessions}


@router.post("/sessions/start")
async def start_session(req: StartSessionRequest, user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    session = mm.episodic.start_session(user["id"], req.session_name, req.clinical_focus)
    return session


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str, req: EndSessionRequest, user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    # Summarize working memory
    summary = req.summary or mm.working.summarize(session_id)
    mm.episodic.end_session(session_id, summary)
    mm.working.clear(session_id)
    return {"success": True}


@router.get("/knowledge-graph")
async def get_knowledge_graph(user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    nodes = mm.semantic.get_nodes(user["id"])
    edges = mm.semantic.get_edges(user["id"])
    return {"nodes": nodes, "edges": edges}


@router.get("/patterns")
async def get_patterns(user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    patterns = mm.procedural.get_patterns(user["id"])
    return patterns


@router.get("/threads")
async def get_threads(user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    threads = mm.episodic.get_research_threads(user["id"])
    return {"threads": threads}

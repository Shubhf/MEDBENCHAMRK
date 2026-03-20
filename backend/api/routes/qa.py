"""Q&A routes with streaming support."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.api.deps import get_current_user, get_llm_router, get_memory_manager
from backend.agents.qa_agent import MedicalQAAgent

router = APIRouter()


class AskRequest(BaseModel):
    query: str
    source_ids: list[str] | None = None
    session_id: str | None = None


@router.post("/ask")
async def ask(req: AskRequest, user: dict = Depends(get_current_user)):
    """Ask a question grounded in your papers."""
    agent = MedicalQAAgent(llm=get_llm_router())
    result = await agent.ask(req.query, user["id"], source_ids=req.source_ids)

    # Log to episodic memory
    mm = get_memory_manager()
    if req.session_id:
        mm.episodic.log_query(
            user["id"], req.session_id, req.query, "qa",
            result.answer, [{"paper": c.paper_title, "quote": c.quote} for c in result.citations],
            result.confidence, req.source_ids or [],
        )

    # Update training data
    mm.update_all(user["id"], {
        "interaction_type": "qa",
        "query_text": req.query,
        "response": result.answer,
        "confidence": result.confidence,
        "session_id": req.session_id or "",
    })

    return {
        "answer": result.answer,
        "citations": [
            {"paper_title": c.paper_title, "section": c.section, "page": c.page, "quote": c.quote}
            for c in result.citations
        ],
        "confidence": result.confidence,
    }


@router.post("/ask/stream")
async def ask_stream(req: AskRequest, user: dict = Depends(get_current_user)):
    """Stream answer tokens via SSE."""
    agent = MedicalQAAgent(llm=get_llm_router())

    async def event_stream():
        async for token in agent.ask_stream(req.query, user["id"], source_ids=req.source_ids):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/history")
async def query_history(user: dict = Depends(get_current_user)):
    mm = get_memory_manager()
    history = mm.episodic.get_query_history(user["id"])
    return {"queries": history}
